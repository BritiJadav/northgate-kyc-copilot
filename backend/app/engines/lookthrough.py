import networkx as nx
from typing import List, Dict, Any, Tuple, Optional, Set
from backend.app.config import settings

class LookThroughResult:
    def __init__(
        self,
        target_company: str,
        effective_owners: List[Dict[str, Any]],
        unresolved_pct: float,
        unresolved_holders: List[Dict[str, Any]],
        has_cycles: bool,
        cycles: List[List[str]],
        graph_nodes: List[Dict[str, Any]],
        graph_edges: List[Dict[str, Any]],
    ):
        self.target_company = target_company
        self.effective_owners = effective_owners
        self.unresolved_pct = unresolved_pct
        self.unresolved_holders = unresolved_holders
        self.has_cycles = has_cycles
        self.cycles = cycles
        self.graph_nodes = graph_nodes
        self.graph_edges = graph_edges

def compute_lookthrough(
    target_company: str,
    edges: List[Dict[str, Any]],
    threshold: float = 25.0,
    merged_aliases: Optional[Dict[str, str]] = None,
    unresolved_entities: Optional[Set[str]] = None
) -> LookThroughResult:
    """
    Deterministic look-through graph engine (Constraint C6).
    Builds the ownership DAG, computes direct and look-through effective percentages
    for all natural persons, detects cycles, and accounts for unresolved holdings.
    """
    merged_aliases = merged_aliases or {}
    unresolved_entities = unresolved_entities or set()

    # Build directed graph: child -> parent (owned -> owner)
    G = nx.DiGraph()

    # Normalize entity names and apply merged aliases if analyst confirmed same person
    cleaned_edges = []
    for e in edges:
        raw_owner = e.get("owner", "").strip()
        raw_owned = e.get("owned", "").strip()
        if not raw_owner or not raw_owned:
            continue

        owner = merged_aliases.get(raw_owner, raw_owner)
        owned = merged_aliases.get(raw_owned, raw_owned)

        pct = e.get("percentage")
        if pct is None and e.get("shares_count") and e.get("total_company_shares"):
            pct = (e["shares_count"] / e["total_company_shares"]) * 100.0
        elif pct is None:
            pct = 0.0

        weight = float(pct) / 100.0
        G.add_edge(owner, owned, weight=weight, percentage=pct)
        cleaned_edges.append({
            "owner": owner,
            "owned": owned,
            "percentage": pct,
            "weight": weight,
            "share_class": e.get("share_class", "Ordinary"),
        })

    # Cycle detection
    cycles = list(nx.simple_cycles(G))
    has_cycles = len(cycles) > 0

    # Find all simple paths from any node to target_company
    # Note: G has edges owner -> owned. So paths go from owner -> ... -> target_company!
    all_owners = [n for n in G.nodes() if n != target_company]
    natural_person_paths: Dict[str, List[Tuple[List[str], float, str]]] = {}

    # Identify intermediate or leaf corporate entities vs terminal natural persons
    for node in all_owners:
        # A node is considered a corporate holder if it has incoming ownership edges
        # (i.e. other owners own shares in it) or if it's explicitly an unresolved entity
        has_upstream_owners = G.in_degree(node) > 0
        is_known_entity = (
            "ltd" in node.lower()
            or "b.v." in node.lower()
            or "s.a." in node.lower()
            or "lp" in node.lower()
            or "nominees" in node.lower()
            or "investments" in node.lower()
            or node in unresolved_entities
        )

        if not has_upstream_owners and not is_known_entity:
            # Terminal natural person candidate
            person = node
            try:
                if nx.has_path(G, person, target_company):
                    paths_to_target = list(nx.all_simple_paths(G, source=person, target=target_company))
                    for path in paths_to_target:
                        # Compute product of weights along this path
                        prod = 1.0
                        formula_parts = []
                        # path is [Person, ..., Target]
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i+1]
                            edge_data = G.get_edge_data(u, v)
                            w = edge_data.get("weight", 0.0)
                            p_pct = edge_data.get("percentage", 0.0)
                            prod *= w
                            formula_parts.append(f"{p_pct:.1f}%")

                        path_pct = prod * 100.0
                        path_formula = " x ".join(formula_parts)
                        if person not in natural_person_paths:
                            natural_person_paths[person] = []
                        natural_person_paths[person].append((path, path_pct, path_formula))
            except Exception:
                pass

    effective_owners = []
    total_effective_identified = 0.0

    for person, path_list in natural_person_paths.items():
        total_pct = sum(p[1] for p in path_list)
        total_effective_identified += total_pct

        if len(path_list) == 1:
            formula = f"{path_list[0][2]} = {total_pct:.2f}%"
        else:
            # Multi-path summation (e.g. Berg via Halden direct + Halden via Norvik)
            parts = [f"({p[2]} = {p[1]:.2f}%)" for p in path_list]
            formula = f"{' + '.join(parts)} = {total_pct:.2f}%"

        is_ubo = total_pct >= threshold

        effective_owners.append({
            "person": person,
            "effective_pct": round(total_pct, 2),
            "is_ubo": is_ubo,
            "formula": formula,
            "paths_count": len(path_list),
            "paths": [
                {"path": p[0], "path_pct": round(p[1], 2), "formula": p[2]}
                for p in path_list
            ],
        })

    # Sort effective owners by percentage descending
    effective_owners.sort(key=lambda x: x["effective_pct"], reverse=True)

    # Compute Unresolved Holdings
    # Any tier-1 holding of target_company that didn't resolve to a natural person
    unresolved_holders = []
    unresolved_pct = 0.0

    tier1_edges = [e for e in cleaned_edges if e["owned"] == target_company]
    for e in tier1_edges:
        holder = e["owner"]
        holder_pct = e["percentage"]
        
        # Check if this holder traces completely to natural persons
        # If holder is nominee, trustee without beneficiaries, or has no upstream owners
        if holder in unresolved_entities or "nominee" in holder.lower() or "trustee" in holder.lower():
            unresolved_pct += holder_pct
            unresolved_holders.append({
                "holder": holder,
                "percent": holder_pct,
                "reason": "Nominee or Trustee holding without disclosed ultimate beneficial owners",
            })
        elif G.in_degree(holder) == 0 and any(kw in holder.lower() for kw in ["ltd", "bvi", "lp", "corp"]):
            unresolved_pct += holder_pct
            unresolved_holders.append({
                "holder": holder,
                "percent": holder_pct,
                "reason": "Corporate entity holding with missing shareholder register",
            })

    # Prepare Graph visualization nodes and edges
    graph_nodes = []
    for node in G.nodes():
        node_type = "target" if node == target_company else ("entity" if ("ltd" in node.lower() or "b.v." in node.lower() or "s.a." in node.lower()) else "person")
        graph_nodes.append({
            "id": node,
            "label": node,
            "type": node_type,
        })

    graph_edges = [
        {
            "source": e["owner"],
            "target": e["owned"],
            "percentage": e["percentage"],
            "label": f"{e['percentage']:.1f}%",
        }
        for e in cleaned_edges
    ]

    return LookThroughResult(
        target_company=target_company,
        effective_owners=effective_owners,
        unresolved_pct=round(unresolved_pct, 2),
        unresolved_holders=unresolved_holders,
        has_cycles=has_cycles,
        cycles=cycles,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
    )

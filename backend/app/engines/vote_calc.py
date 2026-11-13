from typing import List, Dict, Any

class VoteCalculationResult:
    def __init__(
        self,
        total_shares: float,
        total_votes: float,
        shareholders: List[Dict[str, Any]]
    ):
        self.total_shares = total_shares
        self.total_votes = total_votes
        self.shareholders = shareholders

def compute_share_and_voting_rights(
    holdings: List[Dict[str, Any]],
    default_votes_per_share: float = 1.0
) -> VoteCalculationResult:
    """
    Deterministic calculation of equity share percentage vs voting power percentage (Constraint C6).
    Handles multiple share classes with disproportionate voting rights (e.g. Class A 1 vote, Class B 10 votes).
    """
    total_shares = sum(h.get("shares_count", 0.0) or 0.0 for h in holdings)
    
    # Calculate votes per shareholder
    enriched = []
    total_votes = 0.0

    for h in holdings:
        shares = h.get("shares_count", 0.0) or 0.0
        votes_per_share = h.get("votes_per_share")
        if votes_per_share is None:
            votes_per_share = default_votes_per_share
        
        votes = shares * votes_per_share
        total_votes += votes

        enriched.append({
            "owner": h.get("owner"),
            "share_class": h.get("share_class", "Ordinary"),
            "shares_count": shares,
            "votes_per_share": votes_per_share,
            "total_votes": votes,
        })

    # Compute percentages and formula strings
    results = []
    for item in enriched:
        shares = item["shares_count"]
        votes = item["total_votes"]
        vps = item["votes_per_share"]

        share_pct = (shares / total_shares * 100.0) if total_shares > 0 else 0.0
        vote_pct = (votes / total_votes * 100.0) if total_votes > 0 else 0.0

        formula_equity = f"({shares:.0f} shares / {total_shares:.0f} total shares) = {share_pct:.2f}%"
        formula_vote = f"({shares:.0f} shares x {vps:.0f} votes/share) / {total_votes:.0f} total votes = {vote_pct:.2f}%"

        results.append({
            "owner": item["owner"],
            "share_class": item["share_class"],
            "shares_count": shares,
            "votes_per_share": vps,
            "total_votes": votes,
            "share_pct": round(share_pct, 2),
            "vote_pct": round(vote_pct, 2),
            "formula_equity": formula_equity,
            "formula_vote": formula_vote,
            "disproportionate_voting": abs(share_pct - vote_pct) > 1.0,
        })

    return VoteCalculationResult(
        total_shares=total_shares,
        total_votes=total_votes,
        shareholders=results
    )

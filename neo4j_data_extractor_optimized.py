import json
from neo4j import GraphDatabase
import pandas as pd
from typing import Dict, List, Any

class OptimizedPolkadotDataExtractor:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_voting_relationships_batch(self, limit: int = 10000, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Extract voting relationships in batches to avoid memory issues
        """
        with self.driver.session() as session:
            query = """
            MATCH (v:Voter)-[vote:VOTED]->(p:Ref)
            RETURN v.wallet_address as voter_address,
                   v.display_name as voter_name,
                   p.id as proposal_id,
                   p.title as proposal_title,
                   p.tally_ayes as ayes,
                   p.tally_nays as nays,
                   p.status as status,
                   p.requested as requested_amount,
                   vote.decision as vote_type,
                   vote.votingPower as vote_weight
            ORDER BY p.id
            SKIP $skip LIMIT $limit
            """
            
            result = session.run(query, skip=skip, limit=limit)
            relationships = []
            
            for record in result:
                relationships.append({
                    'voter_address': record['voter_address'],
                    'voter_name': record['voter_name'] or '',
                    'proposal_id': record['proposal_id'],
                    'proposal_title': record['proposal_title'],
                    'ayes': int(record['ayes']) if record['ayes'] else 0,
                    'nays': int(record['nays']) if record['nays'] else 0,
                    'status': record['status'],
                    'requested_amount': float(record['requested_amount']) if record['requested_amount'] and record['requested_amount'] != -1 else 0,
                    'vote_type': record['vote_type'],
                    'vote_weight': float(record['vote_weight']) if record['vote_weight'] else 0
                })
            
            return relationships
    
    def get_all_voting_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all voting relationships by processing in batches
        """
        all_relationships = []
        batch_size = 5000  # Smaller batch size to avoid memory issues
        skip = 0
        
        print(f"Extracting voting relationships in batches of {batch_size}...")
        
        while True:
            batch = self.get_voting_relationships_batch(limit=batch_size, skip=skip)
            if not batch:
                break
            
            all_relationships.extend(batch)
            skip += batch_size
            print(f"Extracted {len(all_relationships)} relationships so far...")
            
            # Stop if we have enough for visualization (to avoid memory issues)
            if len(all_relationships) >= 50000:
                print(f"Limiting to {len(all_relationships)} relationships for visualization performance")
                break
        
        return all_relationships
    
    def get_proposal_summary(self) -> List[Dict[str, Any]]:
        """
        Get a summary of all proposals without complex joins
        """
        with self.driver.session() as session:
            query = """
            MATCH (p:Ref)
            RETURN p.id as proposal_id,
                   p.title as proposal_title,
                   p.tally_ayes as ayes,
                   p.tally_nays as nays,
                   p.status as status,
                   p.requested as requested_amount
            ORDER BY p.id
            """
            
            result = session.run(query)
            proposals = []
            
            for record in result:
                proposals.append({
                    'proposal_id': record['proposal_id'],
                    'proposal_title': record['proposal_title'],
                    'ayes': int(record['ayes']) if record['ayes'] else 0,
                    'nays': int(record['nays']) if record['nays'] else 0,
                    'status': record['status'],
                    'requested_amount': float(record['requested_amount']) if record['requested_amount'] and record['requested_amount'] != -1 else 0
                })
            
            return proposals
    
    def get_voter_summary(self) -> List[Dict[str, Any]]:
        """
        Get a summary of voters with their vote counts
        """
        with self.driver.session() as session:
            query = """
            MATCH (v:Voter)-[vote:VOTED]->(p:Ref)
            WITH v, count(vote) as vote_count, avg(vote.votingPower) as avg_voting_power
            RETURN v.wallet_address as voter_address,
                   v.display_name as voter_name,
                   vote_count,
                   avg_voting_power
            ORDER BY vote_count DESC
            LIMIT 1000
            """
            
            result = session.run(query)
            voters = []
            
            for record in result:
                voters.append({
                    'voter_address': record['voter_address'],
                    'voter_name': record['voter_name'] or '',
                    'vote_count': record['vote_count'],
                    'avg_voting_power': record['avg_voting_power']
                })
            
            return voters
    
    def calculate_simple_clusters(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate simple proposal clusters based on shared voters (client-side processing)
        """
        print("Calculating proposal clusters...")
        
        # Group votes by proposal
        proposal_voters = {}
        for rel in relationships:
            prop_id = rel['proposal_id']
            if prop_id not in proposal_voters:
                proposal_voters[prop_id] = set()
            proposal_voters[prop_id].add(rel['voter_address'])
        
        clusters = []
        proposal_ids = list(proposal_voters.keys())
        
        # Compare proposals pairwise (limit to avoid too much computation)
        for i, prop1 in enumerate(proposal_ids[:100]):  # Limit to first 100 proposals
            for prop2 in proposal_ids[i+1:100]:
                if prop1 >= prop2:
                    continue
                
                voters1 = proposal_voters[prop1]
                voters2 = proposal_voters[prop2]
                
                shared = len(voters1.intersection(voters2))
                total = len(voters1.union(voters2))
                
                if total > 0:
                    similarity = shared / total
                    if similarity > 0.1:  # Only include if similarity > 10%
                        # Find proposal titles
                        prop1_title = next((r['proposal_title'] for r in relationships if r['proposal_id'] == prop1), f"Proposal {prop1}")
                        prop2_title = next((r['proposal_title'] for r in relationships if r['proposal_id'] == prop2), f"Proposal {prop2}")
                        
                        clusters.append({
                            'proposal1_id': prop1,
                            'proposal1_title': prop1_title,
                            'proposal2_id': prop2,
                            'proposal2_title': prop2_title,
                            'similarity': similarity
                        })
        
        return sorted(clusters, key=lambda x: x['similarity'], reverse=True)[:50]  # Top 50 clusters

def main():
    # Connection details
    URI = "neo4j+s://56bf968b.databases.neo4j.io"
    USER = "neo4j"
    PASSWORD = "BJX7_gT3khz6BiBezhTrbi-dRl0l-_dfI3fUyuKiX5g"
    
    extractor = OptimizedPolkadotDataExtractor(URI, USER, PASSWORD)
    
    try:
        print("Starting optimized data extraction...")
        
        # Get voting relationships in batches
        relationships = extractor.get_all_voting_relationships()
        
        print("Getting proposal summary...")
        proposals = extractor.get_proposal_summary()
        
        print("Getting voter summary...")
        voters = extractor.get_voter_summary()
        
        print("Calculating clusters...")
        clusters = extractor.calculate_simple_clusters(relationships)
        
        # Prepare data for visualization
        visualization_data = {
            'relationships': relationships,
            'proposals': proposals,
            'voters': voters,
            'clusters': clusters,
            'metadata': {
                'total_relationships': len(relationships),
                'total_proposals': len(proposals),
                'total_voters': len(voters),
                'total_clusters': len(clusters)
            }
        }
        
        # Save to JSON file for the web visualization
        with open('polkadot_voting_data.json', 'w') as f:
            json.dump(visualization_data, f, indent=2)
        
        print(f"\n✅ Data extracted successfully!")
        print(f"- {len(relationships)} voting relationships")
        print(f"- {len(proposals)} proposals")
        print(f"- {len(voters)} voters")
        print(f"- {len(clusters)} proposal clusters")
        print("Data saved to 'polkadot_voting_data.json'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
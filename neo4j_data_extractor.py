import json
from neo4j import GraphDatabase
import pandas as pd
from typing import Dict, List, Any

class PolkadotDataExtractor:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_voting_relationships(self) -> Dict[str, Any]:
        """
        Extract voting relationships between voters and proposals
        """
        with self.driver.session() as session:
            # Query to get all voting relationships
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
            """
            
            result = session.run(query)
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
    
    def get_proposal_clusters(self) -> Dict[str, Any]:
        """
        Calculate proposal clusters based on voting similarity
        """
        with self.driver.session() as session:
            # Query to find proposals with similar voting patterns
            query = """
            MATCH (p1:Ref)<-[:VOTED]-(v:Voter)-[:VOTED]->(p2:Ref)
            WHERE p1.id < p2.id
            WITH p1, p2, count(v) as shared_voters
            MATCH (p1)<-[:VOTED]-(v1:Voter)
            WITH p1, p2, shared_voters, count(v1) as p1_total_voters
            MATCH (p2)<-[:VOTED]-(v2:Voter)
            WITH p1, p2, shared_voters, p1_total_voters, count(v2) as p2_total_voters
            WITH p1, p2, shared_voters, 
                 toFloat(shared_voters) / (p1_total_voters + p2_total_voters - shared_voters) as similarity
            WHERE similarity > 0.1
            RETURN p1.id as proposal1_id,
                   p1.title as proposal1_title,
                   p2.id as proposal2_id,
                   p2.title as proposal2_title,
                   similarity
            ORDER BY similarity DESC
            """
            
            result = session.run(query)
            clusters = []
            
            for record in result:
                clusters.append({
                    'proposal1_id': record['proposal1_id'],
                    'proposal1_title': record['proposal1_title'],
                    'proposal2_id': record['proposal2_id'],
                    'proposal2_title': record['proposal2_title'],
                    'similarity': record['similarity']
                })
            
            return clusters
    
    def get_voter_influence_scores(self) -> Dict[str, Any]:
        """
        Calculate voter influence based on participation and vote alignment with outcomes
        """
        with self.driver.session() as session:
            query = """
            MATCH (v:Voter)-[vote:VOTED]->(p:Ref)
            WITH v, 
                 count(p) as total_votes,
                 sum(CASE 
                     WHEN (vote.decision = 'AYE' AND p.status = 'Executed') OR 
                          (vote.decision = 'NAY' AND p.status IN ['Rejected', 'TimedOut']) 
                     THEN 1 ELSE 0 END) as successful_predictions,
                 avg(vote.votingPower) as avg_vote_weight
            RETURN v.wallet_address as voter_address,
                   v.display_name as voter_name,
                   total_votes,
                   successful_predictions,
                   toFloat(successful_predictions) / total_votes as success_rate,
                   avg_vote_weight,
                   total_votes * (toFloat(successful_predictions) / total_votes) * avg_vote_weight as influence_score
            ORDER BY influence_score DESC
            """
            
            result = session.run(query)
            influences = []
            
            for record in result:
                influences.append({
                    'voter_address': record['voter_address'],
                    'voter_name': record['voter_name'] or '',
                    'total_votes': record['total_votes'],
                    'successful_predictions': record['successful_predictions'],
                    'success_rate': record['success_rate'],
                    'avg_vote_weight': record['avg_vote_weight'],
                    'influence_score': record['influence_score']
                })
            
            return influences

def main():
    # Connection details from your credentials file
    URI = "neo4j+s://56bf968b.databases.neo4j.io"
    USER = "neo4j"
    PASSWORD = "BJX7_gT3khz6BiBezhTrbi-dRl0l-_dfI3fUyuKiX5g"
    
    extractor = PolkadotDataExtractor(URI, USER, PASSWORD)
    
    try:
        print("Extracting voting relationships...")
        relationships = extractor.get_voting_relationships()
        
        print("Calculating proposal clusters...")
        clusters = extractor.get_proposal_clusters()
        
        print("Computing voter influence scores...")
        influences = extractor.get_voter_influence_scores()
        
        # Prepare data for visualization
        visualization_data = {
            'relationships': relationships,
            'clusters': clusters,
            'influences': influences,
            'metadata': {
                'total_relationships': len(relationships),
                'total_clusters': len(clusters),
                'total_voters': len(influences)
            }
        }
        
        # Save to JSON file for the web visualization
        with open('polkadot_voting_data.json', 'w') as f:
            json.dump(visualization_data, f, indent=2)
        
        print(f"Data extracted successfully!")
        print(f"- {len(relationships)} voting relationships")
        print(f"- {len(clusters)} proposal clusters")
        print(f"- {len(influences)} voters with influence scores")
        print("Data saved to 'polkadot_voting_data.json'")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
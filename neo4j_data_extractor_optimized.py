import json
from neo4j import GraphDatabase
import pandas as pd
from typing import Dict, List, Any
import time

class CompletePolkadotDataExtractor:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_voting_relationships_batch(self, limit: int = 5000, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Extract voting relationships in smaller batches to avoid memory issues
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
            ORDER BY p.id, v.wallet_address
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
        Get ALL voting relationships by processing in smaller batches with delays
        """
        all_relationships = []
        batch_size = 3000  # Smaller batch size to avoid memory issues
        skip = 0
        
        print(f"Extracting ALL voting relationships in batches of {batch_size}...")
        print("This will take several minutes to complete...")
        
        while True:
            try:
                print(f"Fetching batch starting at {skip}...")
                batch = self.get_voting_relationships_batch(limit=batch_size, skip=skip)
                
                if not batch:
                    print("No more data found. Extraction complete!")
                    break
                
                all_relationships.extend(batch)
                skip += batch_size
                print(f"✅ Extracted {len(all_relationships)} relationships so far...")
                
                # Add a small delay to avoid overwhelming the database
                time.sleep(0.5)
                
                # Progress indicator every 50k records
                if len(all_relationships) % 50000 == 0:
                    print(f"🎯 Milestone: {len(all_relationships)} relationships extracted!")
                
            except Exception as e:
                print(f"❌ Error in batch starting at {skip}: {e}")
                print("Retrying with smaller batch...")
                # Try with smaller batch if we hit memory limits
                batch_size = max(1000, batch_size // 2)
                time.sleep(2)
                continue
        
        print(f"🎉 Complete! Extracted {len(all_relationships)} total relationships")
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
    
    def get_all_voters_summary(self) -> List[Dict[str, Any]]:
        """
        Get ALL voters with their vote counts (not limited to 1000)
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
    
    def calculate_enhanced_clusters(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate proposal clusters based on shared voters (enhanced version)
        """
        print("Calculating enhanced proposal clusters...")
        
        # Group votes by proposal
        proposal_voters = {}
        for rel in relationships:
            prop_id = rel['proposal_id']
            if prop_id not in proposal_voters:
                proposal_voters[prop_id] = set()
            proposal_voters[prop_id].add(rel['voter_address'])
        
        clusters = []
        proposal_ids = list(proposal_voters.keys())
        
        print(f"Analyzing {len(proposal_ids)} proposals for clustering...")
        
        # Compare proposals pairwise (limit to avoid too much computation)
        max_proposals = min(200, len(proposal_ids))  # Increased from 100 to 200
        for i, prop1 in enumerate(proposal_ids[:max_proposals]):
            if i % 50 == 0:
                print(f"Clustering progress: {i}/{max_proposals} proposals analyzed")
                
            for prop2 in proposal_ids[i+1:max_proposals]:
                if prop1 >= prop2:
                    continue
                
                voters1 = proposal_voters[prop1]
                voters2 = proposal_voters[prop2]
                
                shared = len(voters1.intersection(voters2))
                total = len(voters1.union(voters2))
                
                if total > 0:
                    similarity = shared / total
                    if similarity > 0.05:  # Lowered threshold to 5% for more clusters
                        # Find proposal titles
                        prop1_title = next((r['proposal_title'] for r in relationships if r['proposal_id'] == prop1), f"Proposal {prop1}")
                        prop2_title = next((r['proposal_title'] for r in relationships if r['proposal_id'] == prop2), f"Proposal {prop2}")
                        
                        clusters.append({
                            'proposal1_id': prop1,
                            'proposal1_title': prop1_title,
                            'proposal2_id': prop2,
                            'proposal2_title': prop2_title,
                            'similarity': similarity,
                            'shared_voters': shared,
                            'total_unique_voters': total
                        })
        
        return sorted(clusters, key=lambda x: x['similarity'], reverse=True)[:100]  # Top 100 clusters

def main():
    # Connection details
    URI = "neo4j+s://56bf968b.databases.neo4j.io"
    USER = "neo4j"
    PASSWORD = "BJX7_gT3khz6BiBezhTrbi-dRl0l-_dfI3fUyuKiX5g"
    
    extractor = CompletePolkadotDataExtractor(URI, USER, PASSWORD)
    
    try:
        print("🚀 Starting COMPLETE data extraction...")
        print("This will extract ALL available data from the Neo4j database")
        print("Expected: ~200,000 relationships, ~3,400 voters, ~1,500 proposals")
        print("-" * 60)
        
        # Get ALL voting relationships in batches
        print("\n📊 Step 1: Extracting ALL voting relationships...")
        relationships = extractor.get_all_voting_relationships()
        
        print(f"\n📋 Step 2: Getting all proposals...")
        proposals = extractor.get_proposal_summary()
        print(f"✅ Extracted {len(proposals)} proposals")
        
        print(f"\n👥 Step 3: Getting ALL voters...")
        voters = extractor.get_all_voters_summary()
        print(f"✅ Extracted {len(voters)} voters")
        
        print(f"\n🔗 Step 4: Calculating enhanced clusters...")
        clusters = extractor.calculate_enhanced_clusters(relationships)
        print(f"✅ Calculated {len(clusters)} proposal clusters")
        
        # Prepare complete data for visualization
        visualization_data = {
            'relationships': relationships,
            'proposals': proposals,
            'voters': voters,
            'clusters': clusters,
            'metadata': {
                'total_relationships': len(relationships),
                'total_proposals': len(proposals),
                'total_voters': len(voters),
                'total_clusters': len(clusters),
                'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'data_completeness': 'FULL_DATASET'
            }
        }
        
        # Save to JSON file for the web visualization
        print(f"\n💾 Saving complete dataset to JSON...")
        with open('polkadot_voting_data_complete.json', 'w') as f:
            json.dump(visualization_data, f, indent=2)
        
        print(f"\n🎉 COMPLETE DATA EXTRACTION SUCCESSFUL!")
        print("=" * 60)
        print(f"📊 FINAL STATISTICS:")
        print(f"   • Voting Relationships: {len(relationships):,}")
        print(f"   • Proposals: {len(proposals):,}")
        print(f"   • Voters: {len(voters):,}")
        print(f"   • Proposal Clusters: {len(clusters):,}")
        print(f"📁 Data saved to: 'polkadot_voting_data_complete.json'")
        print(f"📈 Expected file size: ~50-100MB (vs previous 22MB)")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 
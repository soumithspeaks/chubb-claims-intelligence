"""
Agent matching algorithm for waste pickup requests
Implements intelligent agent assignment based on proximity, availability, and performance
"""

import math
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal


class AgentMatcher:
    """
    Intelligent agent matching system for pickup requests
    """
    
    def __init__(self, max_distance_km: float = 10.0, max_agent_load: int = 5):
        """
        Initialize the agent matcher
        
        Args:
            max_distance_km: Maximum distance to search for agents (km)
            max_agent_load: Maximum active pickups per agent
        """
        self.max_distance_km = max_distance_km
        self.max_agent_load = max_agent_load
    
    def find_best_agent(
        self,
        pickup_location: Tuple[float, float],
        available_agents: List[Dict],
        pickup_details: Dict
    ) -> Optional[Dict]:
        """
        Find the best agent for a pickup request
        
        Args:
            pickup_location: (latitude, longitude) of pickup location
            available_agents: List of available agent dictionaries
            pickup_details: Details about the pickup request
            
        Returns:
            Best matched agent or None if no suitable agent found
        """
        if not available_agents:
            return None
        
        # Score each agent
        agent_scores = []
        
        for agent in available_agents:
            score = self._calculate_agent_score(
                agent, 
                pickup_location, 
                pickup_details
            )
            
            if score > 0:  # Only consider agents with positive scores
                agent_scores.append({
                    'agent': agent,
                    'score': score,
                    'distance_km': self._calculate_distance(
                        pickup_location,
                        (agent.get('current_latitude'), agent.get('current_longitude'))
                    )
                })
        
        # Sort by score (descending)
        agent_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Return the best agent
        if agent_scores:
            best_match = agent_scores[0]
            return {
                'agent': best_match['agent'],
                'score': best_match['score'],
                'distance_km': best_match['distance_km'],
                'estimated_arrival_minutes': self._estimate_arrival_time(
                    best_match['distance_km']
                )
            }
        
        return None
    
    def _calculate_agent_score(
        self,
        agent: Dict,
        pickup_location: Tuple[float, float],
        pickup_details: Dict
    ) -> float:
        """
        Calculate a score for an agent based on multiple factors
        
        Higher score = better match
        
        Factors:
        - Distance (closer is better)
        - Agent rating (higher is better)
        - Current load (fewer active pickups is better)
        - Acceptance rate (higher is better)
        """
        # Check if agent has valid location
        if not agent.get('current_latitude') or not agent.get('current_longitude'):
            return 0.0
        
        agent_location = (agent['current_latitude'], agent['current_longitude'])
        distance_km = self._calculate_distance(pickup_location, agent_location)
        
        # Distance score (0-100): closer is better
        if distance_km > self.max_distance_km:
            return 0.0  # Too far
        
        distance_score = (1 - (distance_km / self.max_distance_km)) * 100
        
        # Rating score (0-100): higher rating is better
        rating = float(agent.get('rating', 0))
        total_ratings = agent.get('total_ratings', 0)
        
        if total_ratings > 0:
            rating_score = (rating / 5.0) * 100
        else:
            rating_score = 50  # Neutral score for new agents
        
        # Load score (0-100): fewer active pickups is better
        current_load = agent.get('current_active_pickups', 0)
        if current_load >= self.max_agent_load:
            return 0.0  # Agent is at capacity
        
        load_score = (1 - (current_load / self.max_agent_load)) * 100
        
        # Acceptance rate score (0-100): higher acceptance is better
        total_requests = agent.get('total_requests_received', 0)
        accepted_requests = agent.get('total_requests_accepted', 0)
        
        if total_requests > 0:
            acceptance_rate = accepted_requests / total_requests
            acceptance_score = acceptance_rate * 100
        else:
            acceptance_score = 50  # Neutral score for new agents
        
        # Weighted combination of scores
        # Distance is most important, then rating, then load, then acceptance
        weights = {
            'distance': 0.50,
            'rating': 0.25,
            'load': 0.15,
            'acceptance': 0.10
        }
        
        total_score = (
            distance_score * weights['distance'] +
            rating_score * weights['rating'] +
            load_score * weights['load'] +
            acceptance_score * weights['acceptance']
        )
        
        return total_score
    
    def _calculate_distance(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            location1: (latitude, longitude)
            location2: (latitude, longitude)
            
        Returns:
            Distance in kilometers
        """
        if not location1[0] or not location1[1] or not location2[0] or not location2[1]:
            return float('inf')
        
        lat1, lon1 = location1
        lat2, lon2 = location2
        
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _estimate_arrival_time(self, distance_km: float) -> int:
        """
        Estimate arrival time based on distance
        
        Args:
            distance_km: Distance in kilometers
            
        Returns:
            Estimated time in minutes
        """
        # Assume average speed of 30 km/h in urban areas
        avg_speed_kmh = 30.0
        
        # Add buffer time for traffic and preparation (5 minutes)
        buffer_minutes = 5
        
        travel_time_minutes = (distance_km / avg_speed_kmh) * 60
        total_time = travel_time_minutes + buffer_minutes
        
        return int(math.ceil(total_time))
    
    def optimize_route(
        self,
        agent_location: Tuple[float, float],
        pickup_locations: List[Tuple[float, float]],
        godown_location: Tuple[float, float]
    ) -> List[int]:
        """
        Optimize route for multiple pickups (simple nearest neighbor algorithm)
        For production, use more sophisticated algorithms like TSP solvers
        
        Args:
            agent_location: Current agent location
            pickup_locations: List of pickup locations
            godown_location: Final destination (godown)
            
        Returns:
            List of pickup indices in optimal order
        """
        if not pickup_locations:
            return []
        
        unvisited = list(range(len(pickup_locations)))
        route = []
        current_location = agent_location
        
        # Nearest neighbor algorithm
        while unvisited:
            nearest_idx = None
            nearest_distance = float('inf')
            
            for idx in unvisited:
                distance = self._calculate_distance(
                    current_location,
                    pickup_locations[idx]
                )
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_idx = idx
            
            if nearest_idx is not None:
                route.append(nearest_idx)
                unvisited.remove(nearest_idx)
                current_location = pickup_locations[nearest_idx]
        
        return route
    
    def calculate_estimated_earnings(
        self,
        pickup_payment: Decimal,
        commission_rate: float = 0.20
    ) -> Dict:
        """
        Calculate agent earnings from a pickup
        
        Args:
            pickup_payment: Total payment for the pickup
            commission_rate: Platform commission rate (default 20%)
            
        Returns:
            Dictionary with earnings breakdown
        """
        commission = pickup_payment * Decimal(str(commission_rate))
        agent_earnings = pickup_payment - commission
        
        return {
            'gross_payment': float(pickup_payment),
            'commission': float(commission),
            'agent_earnings': float(agent_earnings),
            'commission_rate': commission_rate
        }


# Example usage
if __name__ == "__main__":
    matcher = AgentMatcher()
    
    # Test data
    pickup_location = (37.7749, -122.4194)  # San Francisco
    
    available_agents = [
        {
            'id': 1,
            'name': 'Agent A',
            'current_latitude': 37.7849,
            'current_longitude': -122.4094,
            'rating': 4.8,
            'total_ratings': 150,
            'current_active_pickups': 2,
            'total_requests_received': 200,
            'total_requests_accepted': 180
        },
        {
            'id': 2,
            'name': 'Agent B',
            'current_latitude': 37.7649,
            'current_longitude': -122.4294,
            'rating': 4.5,
            'total_ratings': 80,
            'current_active_pickups': 1,
            'total_requests_received': 100,
            'total_requests_accepted': 85
        }
    ]
    
    pickup_details = {
        'waste_category': 'Plastic',
        'estimated_weight': 5.0
    }
    
    # Find best agent
    result = matcher.find_best_agent(
        pickup_location,
        available_agents,
        pickup_details
    )
    
    if result:
        print(f"Best Agent: {result['agent']['name']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Distance: {result['distance_km']:.2f} km")
        print(f"ETA: {result['estimated_arrival_minutes']} minutes")
    else:
        print("No suitable agent found")
    
    # Test earnings calculation
    earnings = matcher.calculate_estimated_earnings(Decimal('25.50'))
    print(f"\nEarnings breakdown:")
    print(f"Gross: ${earnings['gross_payment']:.2f}")
    print(f"Commission: ${earnings['commission']:.2f}")
    print(f"Agent earnings: ${earnings['agent_earnings']:.2f}")

import json
import random
import uuid
from flask import jsonify, request
from app.models import prisma

def register_routes(app):
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to Globetrotter API"})
    
    @app.route('/api/destinations/random', methods=['GET'])
    def get_random_destination():
        """Get a random destination with clues for the game"""
        try:
            # Count destinations
            count = prisma.destination.count()
            if count == 0:
                return jsonify({"error": "No destinations found"}), 404
            
            # Get a random destination
            skip = random.randint(0, count - 1)
            destinations = prisma.destination.find_many(take=1, skip=skip)
            if not destinations:
                return jsonify({"error": "No destinations found"}), 404
            
            random_dest = destinations[0]
            
            # Select 1-2 random clues
            num_clues = random.randint(1, min(2, len(random_dest.clues)))
            selected_clues = random.sample(random_dest.clues, num_clues)
            
            # Create response with limited data
            return jsonify({
                "id": random_dest.id,
                "name": random_dest.name,
                "clues": selected_clues
            })
        except Exception as e:
            print(f"Error in random destination: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/destinations/options', methods=['GET'])
    def get_destination_options():
        """Get multiple choice options for a destination"""
        destination_id = request.args.get('destination_id', type=int)
        if not destination_id:
            return jsonify({"error": "destination_id parameter is required"}), 400
        
        # Get the correct destination
        destination = prisma.destination.find_unique(where={"id": destination_id})
        if not destination:
            return jsonify({"error": "Destination not found"}), 404
        
        # Get 3 random wrong options
        all_destinations = prisma.destination.find_many(
            where={"id": {"not": destination_id}}
        )
        
        # Extract just the names
        wrong_options = [dest.name for dest in all_destinations]
        
        # If we have more than 3 wrong options, randomly select 3
        if len(wrong_options) > 3:
            wrong_options = random.sample(wrong_options, 3)
        # If we don't have enough wrong options, add some placeholders
        while len(wrong_options) < 3:
            wrong_options.append(f"Option {len(wrong_options) + 1}")
        
        # Combine correct and wrong options, then shuffle
        all_options = [destination.name] + wrong_options
        random.shuffle(all_options)
        
        return jsonify(all_options)
    
    @app.route('/api/destinations/check-answer', methods=['POST'])
    def check_answer():
        """Check if the submitted answer is correct"""
        data = request.json
        destination_id = data.get('destination_id')
        answer = data.get('answer')
        username = data.get('username')
        gave_up = data.get('gave_up', False)
        tries = data.get('tries', 1)  # Get the number of tries from the request
        
        if not destination_id or (not answer and not gave_up):
            return jsonify({"error": "destination_id and either answer or gave_up are required"}), 400
        
        try:
            destination = prisma.destination.find_unique(where={"id": destination_id})
            if not destination:
                return jsonify({"error": "Destination not found"}), 404
            
            # Normalize answers for comparison (lowercase, remove extra spaces)
            correct_answer = destination.name.lower().strip()
            user_answer = answer.lower().strip() if answer else ""
            
            # Check if answer is correct (exact match or close enough)
            is_correct = correct_answer == user_answer or \
                        (len(user_answer) > 3 and (
                            user_answer in correct_answer or 
                            correct_answer in user_answer or
                            user_answer.split(',')[0].strip() == correct_answer.split(',')[0].strip()
                        ))
            
            # If user gave up, always mark as incorrect
            if gave_up:
                is_correct = False
            
            # Get a random fun fact
            fun_facts = destination.funFacts
            fun_fact = random.choice(fun_facts) if fun_facts else "No fun facts available for this destination."
            
            # Update user stats if username provided
            best_try = None
            if username:
                user = prisma.user.find_unique(where={"username": username})
                if user:
                    # Update stats based on whether answer is correct
                    update_data = {}
                    
                    if is_correct:
                        # Update best try if this is the first correct answer or if tries is better than previous best
                        if user.bestTry == 0 or (tries > 0 and tries < user.bestTry):
                            update_data["bestTry"] = tries
                        
                        # Increment correct answers
                        update_data["correctAnswers"] = user.correctAnswers + 1
                    else:
                        # Increment incorrect answers
                        update_data["incorrectAnswers"] = user.incorrectAnswers + 1
                    
                    # Update user with all changes
                    if update_data:
                        user = prisma.user.update(
                            where={"id": user.id},
                            data=update_data
                        )
                    
                    best_try = user.bestTry
            
            return jsonify({
                "correct": is_correct,
                "correct_answer": destination.name,
                "fun_fact": fun_fact,
                "best_try": best_try,
                "correct_answers": user.correctAnswers if username and user else None,
                "incorrect_answers": user.incorrectAnswers if username and user else None
            })
        except Exception as e:
            app.logger.error(f"Error checking answer: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500
    
    @app.route('/api/users', methods=['POST'])
    def create_user():
        """Create a new user or return existing user"""
        data = request.json
        username = data.get('username')
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        user = prisma.user.find_unique(where={"username": username})
        if user:
            return jsonify({
                "id": user.id,
                "username": user.username,
                "best_try": user.bestTry,
                "correct_answers": user.correctAnswers,
                "incorrect_answers": user.incorrectAnswers
            })
        
        user = prisma.user.create(data={"username": username})
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "best_try": user.bestTry,
            "correct_answers": user.correctAnswers,
            "incorrect_answers": user.incorrectAnswers
        })
    
    @app.route('/api/users/<username>', methods=['GET'])
    def get_user(username):
        """Get user by username"""
        user = prisma.user.find_unique(where={"username": username})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "best_try": user.bestTry,
            "correct_answers": user.correctAnswers,
            "incorrect_answers": user.incorrectAnswers
        })
    
    @app.route('/api/users/challenge', methods=['POST'])
    def create_challenge():
        """Create a new game session for challenging friends"""
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        user = prisma.user.find_unique(where={"id": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate unique invite code
        invite_code = str(uuid.uuid4())[:8]
        
        game_session = prisma.gameSession.create(
            data={
                "inviteCode": invite_code,
                "user": {"connect": {"id": user_id}}
            },
            include={"user": True}
        )
        
        return jsonify({
            "id": game_session.id,
            "invite_code": game_session.inviteCode,
            "user": {
                "id": game_session.user.id,
                "username": game_session.user.username,
                "best_try": game_session.user.bestTry
            }
        })
    
    @app.route('/api/users/challenge/<invite_code>', methods=['GET'])
    def get_challenge(invite_code):
        """Get game session by invite code"""
        game_session = prisma.gameSession.find_unique(
            where={"inviteCode": invite_code},
            include={"user": True}
        )
        
        if not game_session:
            return jsonify({"error": "Challenge not found"}), 404
        
        return jsonify({
            "id": game_session.id,
            "invite_code": game_session.inviteCode,
            "user": {
                "id": game_session.user.id,
                "username": game_session.user.username,
                "best_try": game_session.user.bestTry
            }
        })
    
    @app.route('/api/seed-database', methods=['POST'])
    def seed_database():
        """Endpoint to manually seed the database with initial data"""
        # Load initial destinations from JSON file
        try:
            with open('data/initial_destinations.json', 'r') as f:
                destinations_data = json.load(f)
            
            for dest in destinations_data:
                name = f"{dest['city']}, {dest['country']}"
                
                # Check if destination already exists
                existing = prisma.destination.find_unique(where={"name": name})
                if not existing:
                    prisma.destination.create(
                        data={
                            "name": name,
                            "clues": dest["clues"],
                            "funFacts": dest["fun_fact"],
                            "trivia": dest["trivia"]
                        }
                    )
            
            return jsonify({"message": "Database seeding completed successfully"})
        except Exception as e:
            return jsonify({"error": f"Error seeding database: {str(e)}"}), 500
    
    @app.route('/api/destinations/<int:destination_id>', methods=['GET'])
    def get_destination(destination_id):
        """Get a specific destination by ID"""
        try:
            destination = prisma.destination.find_unique(
                where={"id": destination_id}
            )
            
            if not destination:
                return jsonify({"error": "Destination not found"}), 404
            
            # Create a dictionary with the destination data
            # Use the correct field names from your schema
            destination_dict = {
                "id": destination.id,
                "name": destination.name,
                "clues": destination.clues,
                "funFacts": destination.funFacts
            }
            
            return jsonify(destination_dict)
        except Exception as e:
            app.logger.error(f"Error getting destination {destination_id}: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500
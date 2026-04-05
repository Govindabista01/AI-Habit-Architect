import joblib
import numpy as np
import os
import pandas as pd

class HabitPredictor:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), 'trained', 'habit_predictor.pkl')
        scaler_path = os.path.join(os.path.dirname(__file__), 'trained', 'scaler.pkl')
        features_path = os.path.join(os.path.dirname(__file__), 'trained', 'feature_names.pkl')

        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(features_path)
        except FileNotFoundError:
            print("ERROR: Model files not found. Run retrain_ai_model.py or train_model.py first.")
            self.model = None
            self.scaler = None
            self.feature_names = None

    def predict(self, habit_data):
        if self.model is None or self.scaler is None:
            return {
                'error': 'Model not loaded. Train the model first.',
                'will_complete': False,
                'completion_probability': 0.0,
                'confidence': 'None',
                'probability_percentage': '0.0%'
            }

        import datetime
        today = datetime.datetime.now()
        day_of_week = today.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        num_features = {
            'habit_frequency_per_week': habit_data.get('habit_frequency_per_week', 5),
            'streak_length': habit_data.get('streak_length', 0),
            'completed_days_last_7': habit_data.get('completed_days_last_7', 0),
            'missed_days_last_7': habit_data.get('missed_days_last_7', 0),
            'completion_rate_last_30': habit_data.get('completion_rate_last_30', 0.0),
            'previous_day_completed': habit_data.get('previous_day_completed', 0),
            'motivation_score': habit_data.get('motivation_score', 5),
            'habit_difficulty': habit_data.get('habit_difficulty', 5),
            'is_weekend': is_weekend
        }

        # One-hot encode categorical features (Category and Day of Week)
        category = habit_data.get('habit_category', 'other').lower()
        all_categories = ['health', 'productivity', 'learning', 'mindfulness', 'social', 'finance', 'other']
        all_days = [0, 1, 2, 3, 4, 5, 6]
        
        # Build the full feature row
        features_dict = num_features.copy()
        
        # Add category columns
        for cat in all_categories:
            col_name = f"habit_category_{cat}"
            features_dict[col_name] = 1 if cat == category else 0
            
        # Add day_of_week columns
        for d in all_days:
            col_name = f"day_of_week_{d}"
            features_dict[col_name] = 1 if d == day_of_week else 0
            
        # Convert to DataFrame and reorder columns to match training
        features = pd.DataFrame([features_dict])
        
        # Ensure consistent column ordering (sorted) to match training set
        features = features.reindex(sorted(features.columns), axis=1)

        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0][1]

        if probability >= 0.8 or probability <= 0.2:
            confidence = 'High'
        elif probability >= 0.6 or probability <= 0.4:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        return {
            'will_complete': bool(prediction),
            'completion_probability': round(float(probability), 4),
            'confidence': confidence,
            'probability_percentage': f"{probability * 100:.1f}%"
        }

    def get_category_tips(self, category, probability, streak, motivation, difficulty,
                          completed_last_7, missed_last_7, completion_rate, previous_completed):
        """Return category-specific tips based on habit data"""

        tips = []
        category = category.lower() if category else 'other'

        # ─── HEALTH & FITNESS ───────────────────────────────────────────────
        if category == 'health':
            if probability >= 0.75:
                if streak >= 7:
                    tips.append(f"You have been consistent for {streak} days. Your body is adapting well. Keep going.")
                tips.append("Prepare your workout clothes or equipment tonight for tomorrow.")
                tips.append("Stay hydrated before and after your exercise session.")
                if difficulty >= 7:
                    tips.append("Your fitness habit is intense. Allow proper recovery time between sessions.")
            elif probability >= 0.5:
                tips.append("Do at least 10 minutes of physical activity today even if you feel tired.")
                tips.append("Start with a simple warm-up to get your body moving.")
                if motivation <= 5:
                    tips.append("Low energy today? Try a lighter version of your exercise routine.")
                tips.append("Schedule your workout at a fixed time and treat it like an important meeting.")
            elif probability >= 0.3:
                tips.append("Even a 5 minute walk counts. Start small and build momentum.")
                tips.append("Find a workout partner to keep you accountable today.")
                if missed_last_7 >= 4:
                    tips.append(f"You missed {missed_last_7} days this week. Your fitness progress may decline. Act now.")
                tips.append("Lay out your workout gear right now to remove barriers.")
            else:
                tips.append("Your fitness habit is at critical risk. Do 2 minutes of stretching right now to break the pattern.")
                tips.append("Reflect on why you started this health habit and what you want to achieve.")
                if difficulty >= 8:
                    tips.append("Your routine may be too intense. Consider reducing difficulty to rebuild consistency.")
                tips.append("Track your calories or steps today even if you skip the full workout.")

        # ─── PRODUCTIVITY ────────────────────────────────────────────────────
        elif category == 'productivity':
            if probability >= 0.75:
                if streak >= 14:
                    tips.append(f"Outstanding! {streak} days of consistent productivity. You are building a powerful work ethic.")
                tips.append("Use the Pomodoro technique today: 25 minutes work, 5 minutes break.")
                tips.append("Write your top 3 tasks for today before you start working.")
            elif probability >= 0.5:
                tips.append("Start with your most important task first before checking emails or messages.")
                tips.append("Remove your phone from your workspace for the next 30 minutes.")
                if motivation <= 5:
                    tips.append("Break your work into smaller 15 minute chunks to build momentum.")
                tips.append("Set a timer and commit to working without interruption for just 20 minutes.")
            elif probability >= 0.3:
                tips.append("Close all social media tabs and unnecessary browser windows right now.")
                if completed_last_7 <= 2:
                    tips.append(f"You only completed this {completed_last_7} times this week. Identify what is blocking you.")
                tips.append("Work in a different location today to reset your focus.")
                tips.append("Tell someone your goal for today to create accountability.")
            else:
                tips.append("Your productivity habit is failing. Do one small task right now, even 5 minutes.")
                tips.append("Identify the biggest distraction in your environment and eliminate it.")
                if difficulty >= 8:
                    tips.append("The task may feel overwhelming. Break it into the smallest possible first step.")
                tips.append("Review your goals and remind yourself why this productivity habit matters.")

        # ─── LEARNING ────────────────────────────────────────────────────────
        elif category == 'learning':
            if probability >= 0.75:
                if streak >= 7:
                    tips.append(f"Excellent! {streak} days of continuous learning. Consistency is the key to mastery.")
                tips.append("Review what you learned yesterday before starting today's session.")
                tips.append("Try to teach someone what you learned today. Teaching reinforces memory.")
            elif probability >= 0.5:
                tips.append("Set a specific learning goal for today. For example: complete one chapter or lesson.")
                tips.append("Find a quiet place with no distractions for your study session.")
                if motivation <= 5:
                    tips.append("Watch a short inspiring video about your learning topic to reignite your curiosity.")
                tips.append("Use active recall: close your notes and try to remember what you studied.")
            elif probability >= 0.3:
                tips.append("Even 15 minutes of focused learning is better than skipping entirely.")
                if completion_rate < 0.4:
                    tips.append(f"Your 30-day completion rate is only {int(completion_rate*100)}%. Try studying at the same time every day.")
                tips.append("Listen to a podcast or watch a video related to your learning topic while commuting.")
                tips.append("Remove distractions by using apps like Forest or StayFocusd while studying.")
            else:
                tips.append("Your learning habit is at critical risk. Open your book or course material right now.")
                tips.append("Set a very small goal: read just one page or watch just 5 minutes of a lesson.")
                if difficulty >= 8:
                    tips.append("The material may be too complex. Find a simpler resource to rebuild confidence.")
                tips.append("Remember: missing learning sessions creates knowledge gaps that are hard to recover.")

        # ─── MINDFULNESS ─────────────────────────────────────────────────────
        elif category == 'mindfulness':
            if probability >= 0.75:
                if streak >= 10:
                    tips.append(f"Beautiful! {streak} days of mindfulness practice. Your mental clarity is growing.")
                tips.append("Try extending your session by 5 minutes today to deepen your practice.")
                tips.append("Keep a mindfulness journal to track your mental state and progress.")
            elif probability >= 0.5:
                tips.append("Find a quiet spot and take 5 deep breaths right now to get started.")
                tips.append("Set a gentle timer so you are not worried about time during your session.")
                if motivation <= 5:
                    tips.append("Use a guided meditation app like Headspace or Calm to help you focus today.")
                tips.append("Even 5 minutes of mindfulness has measurable benefits for stress and focus.")
            elif probability >= 0.3:
                tips.append("Take 3 deep breaths right now. You have already started your mindfulness practice.")
                if missed_last_7 >= 3:
                    tips.append("You have missed several sessions. Stress may be building up. Take time for yourself today.")
                tips.append("Practice mindful eating during your next meal as a simple alternative today.")
                tips.append("Reduce screen time by 30 minutes today and use that time for quiet reflection.")
            else:
                tips.append("Your mindfulness habit is at critical risk. Sit quietly for just 2 minutes with your eyes closed.")
                tips.append("High stress may be preventing your practice. Start with box breathing: 4 counts in, hold, out, hold.")
                if difficulty >= 7:
                    tips.append("Mindfulness does not need to be formal. Try a mindful walk outside today instead.")
                tips.append("Your mental health depends on this habit. Prioritize it above other tasks today.")

        # ─── SOCIAL ──────────────────────────────────────────────────────────
        elif category == 'social':
            if probability >= 0.75:
                if streak >= 5:
                    tips.append(f"Great social consistency over {streak} days. Your relationships are growing stronger.")
                tips.append("Reach out to someone you have not spoken to in a while today.")
                tips.append("Plan a specific social activity for this week to maintain momentum.")
            elif probability >= 0.5:
                tips.append("Send a message or make a call to one person today. Even a short check-in counts.")
                tips.append("Schedule social time in your calendar like any other important appointment.")
                if motivation <= 5:
                    tips.append("Social connection improves mood. Push yourself to reach out even if you feel introverted today.")
                tips.append("Join an online community or group related to your interests today.")
            elif probability >= 0.3:
                tips.append("Text one friend or family member right now. It takes less than a minute.")
                if completed_last_7 <= 2:
                    tips.append("You have been socially withdrawn this week. Isolation affects mental health. Reach out today.")
                tips.append("Attend a social event or activity this week to reconnect with others.")
                tips.append("Social habits build support networks. These networks help you with all your other habits.")
            else:
                tips.append("Your social habit is at critical risk. Send one message to anyone you care about right now.")
                tips.append("Prolonged isolation can increase anxiety and reduce motivation for all habits.")
                if difficulty >= 7:
                    tips.append("If social interaction feels difficult, start with a simple emoji reaction to someone's post.")
                tips.append("Consider whether stress or anxiety is preventing social connection and seek support if needed.")

        # ─── FINANCE ─────────────────────────────────────────────────────────
        elif category == 'finance':
            if probability >= 0.75:
                if streak >= 7:
                    tips.append(f"Excellent financial discipline over {streak} days. Your future self will thank you.")
                tips.append("Review your savings goal today and calculate how close you are to achieving it.")
                tips.append("Consider automating your savings or investment contributions to maintain consistency.")
            elif probability >= 0.5:
                tips.append("Track every expense today. Awareness is the first step to financial discipline.")
                tips.append("Review your budget and identify one unnecessary expense you can cut this week.")
                if motivation <= 5:
                    tips.append("Visualize your financial goal: a house, travel, or retirement. Let that motivate you today.")
                tips.append("Set a specific savings target for this week and write it down.")
            elif probability >= 0.3:
                tips.append("Open your banking app right now and check your balance and recent spending.")
                if completion_rate < 0.4:
                    tips.append(f"Your 30-day financial habit rate is only {int(completion_rate*100)}%. Small daily actions build big financial results.")
                tips.append("Avoid impulse purchases today. Wait 24 hours before buying anything non-essential.")
                tips.append("Read one article about personal finance or investing today to rebuild motivation.")
            else:
                tips.append("Your finance habit is at critical risk. Record just one expense or saving right now.")
                tips.append("Financial habits compound over time. Every day you skip costs you in the long run.")
                if difficulty >= 8:
                    tips.append("Managing finances feels overwhelming? Start with just tracking one category of spending.")
                tips.append("Consider using a budgeting app like YNAB or Mint to make the habit easier.")

        # ─── OTHER ───────────────────────────────────────────────────────────
        else:
            if probability >= 0.75:
                if streak >= 7:
                    tips.append(f"You have maintained this habit for {streak} days. Your consistency is paying off.")
                tips.append("Keep your environment set up to support this habit every day.")
                tips.append("Link this habit to another habit you always do to make it automatic.")
            elif probability >= 0.5:
                tips.append("Set a specific time today for this habit and put it in your schedule.")
                tips.append("Prepare everything you need for this habit before you go to sleep tonight.")
                if motivation <= 5:
                    tips.append("Remind yourself of the long-term benefits this habit brings to your life.")
                tips.append("Start with just 2 minutes of this habit to overcome resistance.")
            elif probability >= 0.3:
                tips.append("Do not skip today. Missing two days in a row breaks habits faster than anything.")
                if missed_last_7 >= 4:
                    tips.append(f"You missed {missed_last_7} days this week. Today is critical for recovery.")
                tips.append("Tell someone close to you that you will complete this habit today.")
                tips.append("Reduce the difficulty of the habit temporarily to rebuild your streak.")
            else:
                tips.append("Act immediately. Do the smallest version of this habit right now.")
                tips.append("Identify what is blocking you from doing this habit and remove that obstacle today.")
                if difficulty >= 8:
                    tips.append("The habit may be too hard right now. Scale it down until consistency returns.")
                tips.append("Review your reason for starting this habit and reconnect with your original motivation.")

        return tips

    def get_recommendation(self, prediction_result, habit_data):
        """Generate fully personalized recommendation based on category and individual habit data"""

        probability = prediction_result['completion_probability']
        streak = habit_data.get('streak_length', 0)
        motivation = habit_data.get('motivation_score', 5)
        difficulty = habit_data.get('habit_difficulty', 5)
        completed_last_7 = habit_data.get('completed_days_last_7', 0)
        missed_last_7 = habit_data.get('missed_days_last_7', 0)
        completion_rate = habit_data.get('completion_rate_last_30', 0.0)
        previous_completed = habit_data.get('previous_day_completed', 0)
        category = habit_data.get('habit_category', 'other')
        habit_name = habit_data.get('habit_name', 'this habit')

        # Risk level and message based on probability
        if probability >= 0.75:
            risk_level = 'Low'
            message = f"You are highly likely to complete {habit_name} today. Your consistency is building a strong foundation."

        elif probability >= 0.5:
            risk_level = 'Medium'
            message = f"{habit_name} has a moderate chance of completion today. Stay focused and committed to finish it."

        elif probability >= 0.3:
            risk_level = 'High'
            message = f"{habit_name} is at risk today. Based on your recent behavior, you need to take action now."

        else:
            risk_level = 'Critical'
            message = f"{habit_name} is in critical danger today. Your behavioral data shows a strong pattern of missing. Break that pattern now."

        # Get category specific tips
        tips = self.get_category_tips(
            category, probability, streak, motivation, difficulty,
            completed_last_7, missed_last_7, completion_rate, previous_completed
        )

        # Add streak specific tip at the end if not already mentioned
        if streak == 0 and previous_completed == 0:
            tips.append("You missed yesterday. Starting fresh today will reset your momentum positively.")
        elif streak >= 30 and risk_level in ['High', 'Critical']:
            tips.append(f"Warning: Your {streak} day streak is about to break. Do not let it end today.")

        return {
            'message': message,
            'tips': tips[:5],
            'risk_level': risk_level
        }


# Test all categories
if __name__ == "__main__":
    predictor = HabitPredictor()

    test_habits = [
        {
            'habit_name': 'Morning Run',
            'habit_category': 'health',
            'habit_frequency_per_week': 7,
            'streak_length': 12,
            'completed_days_last_7': 6,
            'missed_days_last_7': 1,
            'completion_rate_last_30': 0.85,
            'previous_day_completed': 1,
            'motivation_score': 8,
            'habit_difficulty': 6
        },
        {
            'habit_name': 'Deep Work Session',
            'habit_category': 'productivity',
            'habit_frequency_per_week': 5,
            'streak_length': 0,
            'completed_days_last_7': 2,
            'missed_days_last_7': 5,
            'completion_rate_last_30': 0.30,
            'previous_day_completed': 0,
            'motivation_score': 4,
            'habit_difficulty': 7
        },
        {
            'habit_name': 'Study Python',
            'habit_category': 'learning',
            'habit_frequency_per_week': 5,
            'streak_length': 5,
            'completed_days_last_7': 4,
            'missed_days_last_7': 3,
            'completion_rate_last_30': 0.60,
            'previous_day_completed': 1,
            'motivation_score': 7,
            'habit_difficulty': 6
        },
        {
            'habit_name': 'Meditation',
            'habit_category': 'mindfulness',
            'habit_frequency_per_week': 7,
            'streak_length': 0,
            'completed_days_last_7': 1,
            'missed_days_last_7': 6,
            'completion_rate_last_30': 0.20,
            'previous_day_completed': 0,
            'motivation_score': 3,
            'habit_difficulty': 5
        },
        {
            'habit_name': 'Save Money',
            'habit_category': 'finance',
            'habit_frequency_per_week': 7,
            'streak_length': 20,
            'completed_days_last_7': 7,
            'missed_days_last_7': 0,
            'completion_rate_last_30': 0.92,
            'previous_day_completed': 1,
            'motivation_score': 9,
            'habit_difficulty': 4
        }
    ]

    for habit in test_habits:
        print(f"\n{'='*60}")
        print(f"Habit: {habit['habit_name']} ({habit['habit_category']})")
        print('='*60)
        result = predictor.predict(habit)
        rec = predictor.get_recommendation(result, habit)
        print(f"Probability: {result['probability_percentage']}")
        print(f"Risk Level: {rec['risk_level']}")
        print(f"Message: {rec['message']}")
        print("Tips:")
        for i, tip in enumerate(rec['tips'], 1):
            print(f"  {i}. {tip}")
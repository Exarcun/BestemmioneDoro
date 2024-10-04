import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import os
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# File to store used words
WORDS_FILE = 'used_words.txt'

# Message counter
message_counter = 0

# Custom responses for each score
score_responses = {
    1: "😡 Ma che cazzo di bestemmia è ❌",
    2: "😐 Chi cazzo ti ha insegnato a bestemmiare 😡 ",
    3: " 🚬 Un po' più di impegno 🍸",
    4: "🤔 Ci sei quasi 🤔",
    5: " 😎 Mediocre Bestemmia 😎",
    6: " 🫡 Bravo bestemmiatore 🫡",
    7: "🔊Bestemmia impressionante 🔊",
    8: " 🍾è quasi morto il papa dopo questa 🍿",
    9: " 👹👺PORCO DIO! SIAMO A LIVELLI ESTREMI DI BESTEMMIA! 👹",
    10: "il diavolo"
}

# Function to load used words from file
def load_used_words():
    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, 'r') as f:
            return set(word.strip() for word in f)
    return set()

# Function to save used words to file
def save_used_words(used_words):
    with open(WORDS_FILE, 'w') as f:
        for word in used_words:
            f.write(f"{word}\n")

# Function to load the leaderboard
def load_leaderboard():
    if os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'r') as f:
            return json.load(f)
    return {}

# Function to save the leaderboard
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

# Function to calculate total global score
def get_global_score():
    leaderboard = load_leaderboard()
    return sum(leaderboard.values())

# Function to handle the /start command
async def start(update: Update, context):
    await update.message.reply_text('Bestemmiometro ON ❌ ┌∩┐(◣ _ ◢)┌∩┐ ✝️')

# Function to handle messages
async def handle_message(update: Update, context):
    global message_counter
    message = update.message.text.lower()
    
    if message.startswith('dio'):
        words = message.split()
        used_words = load_used_words()
        
        # Check if the message is longer than 10 words
        if len(words) > 10:
            score = 1
        else:
            words = words[1:5]  # Get only the first 4 words after "orzo"
            score = 1  # Start with 1 point for using "orzo"
            new_words = []
            
            for word in words:
                if word not in used_words:
                    score += 2
                    used_words.add(word)
                    new_words.append(word)
                else:
                    score += 1
        
        # Cap the score at 9 (maximum possible score: 1 for orzo + 4*2 for new words)
        score = min(score, 9)
        
        # Save the updated used words
        save_used_words(used_words)
        
        # Update leaderboard
        user_id = update.effective_user.id
        username = update.effective_user.username or str(user_id)
        leaderboard = load_leaderboard()
        leaderboard[username] = leaderboard.get(username, 0) + score
        save_leaderboard(leaderboard)
        
        # Determine if we should respond based on the score
        should_respond = score >= 7 or (score < 7 and random.random() < 0.5)
        
        if should_respond:
            # Prepare response message
            response = f"{score_responses[score]}\n"
            response += f"Bestemmiometro: {score}/9\n"
            if new_words:
                response += f"Nuove bestemmie: {', '.join(new_words)}\n"
            response += "Punteggio aggiunto '!👺 per visualizzare'"
            
            await update.message.reply_text(response)
            
            message_counter += 1
            if message_counter % 10 == 0:
                await show_global_score(update, context)
    
    elif message == "!👺":
        await show_leaderboard(update, context)
    
    elif message == "!👹":
        await show_global_score(update, context)

# Function to handle the !👺 command
async def show_leaderboard(update: Update, context):
    leaderboard = load_leaderboard()
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    response = "🏆 Classifica dei Bestemmiatori 🏆\n\n"
    
    for i, (username, score) in enumerate(sorted_leaderboard[:5], 1):
        response += f"{i}. {username}: {score} punti\n"
    
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)
    
    user_rank = next((i for i, (name, _) in enumerate(sorted_leaderboard, 1) if name == username), None)
    
    if user_rank and user_rank > 5:
        response += f"\nLa tua posizione:\n{user_rank}. {username}: {leaderboard[username]} punti"
    
    await update.message.reply_text(response)

# Function to show global score
async def show_global_score(update: Update, context):
    global_score = get_global_score()
    await update.message.reply_text(f"👺 Bestemmiometro: {global_score} 🍾 🔥 ┌∩┐(◣ _ ◢)┌∩┐ 🔥✝️🔥")

def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token('7542914299:AAHXQN00FM1KoyxFXyyI0nhCaEVgy0EeRSs').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
import json
import os
import time
import random
import sys
import pygame
import msvcrt

def resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller bundles."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- AUDIO & CONFIG UTILITIES ---
AUDIO_ENABLED = True
try:
    pygame.mixer.init()
except (pygame.error, NotImplementedError, ModuleNotFoundError):
    AUDIO_ENABLED = False

CURRENT_TRACK = None

def play_audio_track(filename):
    global CURRENT_TRACK
    if not AUDIO_ENABLED:
        return
    # If this exact track is already playing, do nothing so it doesn't restart!
    if CURRENT_TRACK == filename and pygame.mixer.music.get_busy():
        return
    try:
        path = resource_path(os.path.join("assets", filename))
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
        CURRENT_TRACK = filename
    except pygame.error:
        pass

def play_sfx(filename):
    """Safely plays a short sound effect from the assets folder."""
    if not AUDIO_ENABLED:
        return
    try:
        path = resource_path(os.path.join("assets", filename))
        sound = pygame.mixer.Sound(path)
        sound.play()
    except pygame.error:
        pass # Fails silently if the sfx file is missing

SAVE_FILE = "lexicon.json" 
COLOR_DEFAULT = "\033[0m" 
COLOR_ABYSS = "\033[94m"    
COLOR_SYSTEM = "\033[96m"   
COLOR_CLUE = "\033[93m"     
COLOR_DANGER = "\033[91m"   
COLOR_VICTORY = "\033[92m"  

def type_text(text, speed=0.015, color=COLOR_DEFAULT, corrupt=False): 
    """Outputs text with typewriter effect letter-by-letter and optional 'madness' corruption."""
    sys.stdout.write(color) 
    for char in text: 
        if corrupt and random.random() < 0.08: 
            sys.stdout.write(random.choice(["~", "≈", "§", "?", "∆"]))
        else:
            sys.stdout.write(char) 
        sys.stdout.flush() # Forces Python to display the character immediately
        time.sleep(speed) 
    sys.stdout.write(COLOR_DEFAULT + "\n") 
    sys.stdout.flush()

def clear_input_buffer():
    """Clears any lingering keystrokes in the Windows input buffer."""
    if os.name == 'nt':
        while msvcrt.kbhit():
            msvcrt.getch()

def clear_screen(): 
    os.system('cls' if os.name == 'nt' else 'clear') 

# --- ROGUELITE META-PROGRESSION (GAME 1) ---
def load_lexicon(): 
    if os.path.exists(SAVE_FILE): 
        with open(SAVE_FILE, 'r') as f: 
            try:
                return json.load(f) 
            except json.JSONDecodeError:
                return []
    return [] 

def save_lexicon(lexicon): 
    with open(SAVE_FILE, 'w') as f: 
        json.dump(lexicon, f) 

# --- TUTORIAL SYSTEM ---
def show_tutorial():
    play_audio_track("title_music.mp3")
    clear_screen()
    print(COLOR_SYSTEM + "=" * 70)
    print("\n" + " " * 24 + "G A M E   T U T O R I A L\n")
    print("=" * 70 + COLOR_DEFAULT)
    
    print(COLOR_CLUE + "\n1. THE SALT TIDE (Social Deduction Horror):" + COLOR_DEFAULT)
    print("   - You have 5 cycles before the tide consumes the ziggurat.")
    print("   - Explore locations (The Slums, Archives, Foundry) to uncover clues. Uncovering clues can lead to new areas, and you may check your clues at the entrance.")
    print("   - Each suspect (High Priest, Bronze Smith, Concubine) may be a Sea Thrall. Only one is the true Sea Thrall.")
    print("   - Acquiring clues may increase your Terror; at 100%, you keel over in madness. Meditate to reduce Terror.")
    print("   - Accuse the correct Sea Thrall at the Foundry before time runs out to win.")
    
    print(COLOR_CLUE + "\n2. THE EMPTIED FORM (Recursive Exploration):" + COLOR_DEFAULT)
    print("   - Traverse through abstract, shifting rooms using directional choices.")
    print("   - Find the way out.")
    print("   - Was there ever a way out?")
    
    input(COLOR_CLUE + "\n[Press Enter to return to the Compilation Menu]" + COLOR_DEFAULT)
    play_sfx("click.wav")

# --- GAME 1: THE SALT TIDE ---
def show_salt_tide_title():
    play_audio_track("title_music.mp3")
    clear_screen()
    print(COLOR_ABYSS + "=" * 70)
    print("\n" + " " * 22 + "T H E   S A L T   T I D E\n")
    print("=" * 70 + COLOR_DEFAULT)
    print(" " * 22 + "A Bronze Age Psychological Horror\n")
    
    print(COLOR_SYSTEM + " " * 28 + "CREDITS" + COLOR_DEFAULT)
    print(" " * 21 + "Lead Developer & Designer: Team MS-FF")
    print("\n" + COLOR_ABYSS + "=" * 70 + COLOR_DEFAULT)
    
    input(COLOR_CLUE + "\n" + " " * 19 + "[Press Enter to face the Tide]" + COLOR_DEFAULT)
    play_sfx("click.wav")

def run_salt_tide():
    show_salt_tide_title()
    play_audio_track("ambience.mp3") 
    clear_screen() 
    lexicon = load_lexicon() 
    days_remaining = 5 
    terror = 0
    current_location = "Ziggurat Entrance" 
    
    suspects = ["High Priest", "Bronze Smith", "Concubine"] 
    sea_thrall = random.choice(suspects) 
    
    type_text("WAKING UP IN COLD SWEAT...", color=COLOR_SYSTEM)
    time.sleep(1) 
    
    while days_remaining > 0: 
        clear_screen() 
        type_text(f"--- {current_location.upper()} ---", color=COLOR_SYSTEM) 
        type_text(f"Cycles until the Tide Consumes Us: {days_remaining}", color=COLOR_ABYSS)
        type_text(f"Current Terror Level: {terror}%", color=COLOR_DANGER)
        print("\n") 
        
        if current_location == "Ziggurat Entrance": 
            type_text("The monsoon rains are tearing at the mud-brick steps, but it's the wind that has everyone terrified. It smells like deep water and dead things. The heavy Bronze Doors lead into the Archives. Down the slick steps, The Slums are drowning in the deluge.")
            print("\n1. Speak to the High Priest") 
            print("2. Travel to The Slums") 
            # FIXED: Unlocks if you have ANY clue in your lexicon, preventing deadlocks
            if len(lexicon) > 0:
                print(f"3. {COLOR_CLUE}[UNLOCK]{COLOR_DEFAULT} Open the Bronze Doors to The Archives") 
            else:
                print(f"3. {COLOR_DANGER}[LOCKED]{COLOR_DEFAULT} Open the Bronze Doors to The Archives (Requires a discovered clue)")
            print("4. Meditate at the inner shrine (Calm your mind [-15% Terror, -1 Cycle])")
            print("5. Inspect your Lexicon of Forbidden Knowledge")
            print("6. Scrutinize the outer wall carvings (Gain an initial lead)") # Alternative early clue source
            clear_input_buffer()
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
            if choice == "1": 
                if sea_thrall == "High Priest":
                    type_text("He grabs your shoulders, his fingernails digging painfully into your skin. 'They ride on the backs of dead trees! Trees that don't sink! The gods have abandoned the water! We are already dead!' he sobs.", color=COLOR_ABYSS, corrupt=True)
                    terror += 20
                    play_sfx("terror_spike.wav")
                else:
                    type_text("He rubs his temples, looking exhausted. 'The pantheon is quiet today. But the walls are thick. Keep your head down and trust the ziggurat.'")
                    terror += 5
                input("\n[Press Enter]") 
                play_sfx("click.wav")
                days_remaining -= 1 
            elif choice == "2": 
                current_location = "The Slums" 
            elif choice == "3" and len(lexicon) > 0:
                current_location = "The Archives" 
            elif choice == "4": 
                if terror > 0:
                    terror = max(0, terror - 15)
                    type_text("You burn sweet-smelling cedar and press your forehead against the cool stone wall. The panic recedes slightly from your chest.", color=COLOR_VICTORY)
                    play_sfx("clue_unlock.wav")
                else:
                    type_text("Your mind is already clear of panic.")
                input("\n[Press Enter]")
                play_sfx("click.wav")
                days_remaining -= 1
            elif choice == "5": 
                clear_screen()
                type_text("--- YOUR UNLOCKED LEXICON ---", color=COLOR_SYSTEM)
                if not lexicon:
                    type_text("Your mind is currently clean of forbidden revelations. No clues recorded.", color=COLOR_DEFAULT)
                else:
                    for idx, clue in enumerate(lexicon, 1):
                        formatted_clue = clue.replace("_", " ").title()
                        type_text(f"{idx}. [UNLOCKED] {formatted_clue}", color=COLOR_CLUE)
                input("\n[Press Enter to return]")
                play_sfx("click.wav")
            elif choice == "6":
                if "ziggurat_foundation_lore" not in lexicon:
                    type_text("You inspect the water-damaged brickwork. Ancient glyphs speak of a time before the bronze walls, when the city traded with outsiders across the roaring deep. A strange realization dawns on you.", color=COLOR_CLUE)
                    lexicon.append("ziggurat_foundation_lore")
                    save_lexicon(lexicon)
                    terror += 25
                    play_sfx("clue_unlock.wav")
                else:
                    type_text("You've already studied these carvings as closely as you can bear.")
                    terror += 5
                input("\n[Press Enter]")
                play_sfx("click.wav")
                days_remaining -= 1
        
        elif current_location == "The Slums": 
            type_text("The air here is choked with ash, poverty, and sheer panic. An old beggar sits in the muck, weeping as he scratches impossible shapes into the clay. The Foundry looms ahead, sealed off by the priests with a wall of sacred fire to keep 'the corruption' out.")
            print("\n1. Listen to the Beggar") 
            print("2. Return to Ziggurat") 
            # FIXED: Unlocks if you have ANY clue in your lexicon
            if len(lexicon) > 0:
                print(f"3. {COLOR_CLUE}[UNLOCK]{COLOR_DEFAULT} Part the fire and enter The Foundry") 
            else:
                print(f"3. {COLOR_DANGER}[LOCKED]{COLOR_DEFAULT} Part the fire and enter The Foundry (Requires a discovered clue)")
            clear_input_buffer()   
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
            if choice == "1": 
                if "concept_of_the_floating_wood" not in lexicon:
                    type_text("The beggar grabs your ankle. He rambles about 'wood that floats heavily'. As you picture a massive tree carrying men across the ocean, a sickening headache hits you. You grasp the 'Concept of the Floating Wood'. Your nose starts bleeding.", color=COLOR_CLUE)
                    lexicon.append("concept_of_the_floating_wood")
                    save_lexicon(lexicon) 
                    terror += 40
                    play_sfx("clue_unlock.wav")
                else:
                    type_text("He just rocks back and forth, muttering about shadows upon the waves. You can't bear to listen to it again.")
                    terror += 10
                input("\n[Press Enter]") 
                play_sfx("click.wav")
                days_remaining -= 1 
            elif choice == "2": 
                current_location = "Ziggurat Entrance" 
            elif choice == "3" and len(lexicon) > 0:
                current_location = "The Foundry" 

        elif current_location == "The Archives": 
            type_text("Total chaos. Scribes are frantically smashing their own clay tablets, screaming that the foreign descriptions are infecting the holy texts. The Concubine stands alone among the debris, calmly reading a glowing shard.")
            print("\n1. Speak to the Concubine") 
            print("2. Read the glowing central tablet") 
            print("3. Return to Ziggurat") 
            clear_input_buffer()
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
            if choice == "1": 
                if sea_thrall == "Concubine":
                    type_text("She smiles, but her eyes are completely vacant. 'I heard them shouting from the shores. It isn't a language... it's just violence. Grunts and harsh barking. It unmade my mind just hearing it. It's beautiful.'", color=COLOR_ABYSS, corrupt=True)
                    terror += 20
                    play_sfx("terror_spike.wav")
                else:
                    type_text("She steps over a shattered tablet. 'They are burning the records to hide the truth. Don't trust the Smith—I heard he's been trying to copy their terrible weapons.'")
                    terror += 5
                input("\n[Press Enter]") 
                play_sfx("click.wav")
                days_remaining -= 1 
            elif choice == "2": 
                if "the_iron_heresy" not in lexicon:
                    type_text("You pick up the shard. It describes the 'Iron Heresy': swords forged not from sacred, beautiful bronze, but from vulgar, gray dirt. The implications make you want to throw up.", color=COLOR_CLUE)
                    lexicon.append("the_iron_heresy")
                    save_lexicon(lexicon) 
                    terror += 40
                    play_sfx("clue_unlock.wav")
                else:
                    type_text("Just shards of broken history. Nothing you don't already know.")
                    terror += 10
                input("\n[Press Enter]") 
                play_sfx("click.wav")
                days_remaining -= 1 
            elif choice == "3": 
                current_location = "Ziggurat Entrance" 

        elif current_location == "The Foundry": 
            type_text("The heat is suffocating, baking the sweat right off your skin. The Bronze Smith is hunched over his anvil, shivering despite the fire, striking a strange, gray metal that simply shouldn't exist.")
            print("\n1. Speak to the Bronze Smith") 
            print("2. Accuse a suspect of being a Sea Thrall")
            print("3. Return to The Slums") 
            clear_input_buffer()
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
            if choice == "1": 
                if sea_thrall == "Bronze Smith":
                    type_text("He throws his hammer across the room. 'It's dirt! They make their swords out of dirt, and it shatters our bronze! The geometry is wrong! It defies the gods! It's all wrong!' he screams, tearing at his hair.", color=COLOR_ABYSS, corrupt=True)
                    terror += 20
                    play_sfx("terror_spike.wav")
                else:
                    type_text("He wipes soot from his face. 'I saw the Concubine in the Archives before the scribes went mad. She was reading the forbidden tide-charts.'")
                    terror += 5
                input("\n[Press Enter]") 
                play_sfx("click.wav")
                days_remaining -= 1 
            elif choice == "2": 
                print("\nWho has succumbed to the madness of the Sea People?")
                for i, suspect in enumerate(suspects): 
                    print(f"{i+1}. {suspect}") 
                
                try: 
                    accused_input = input("> ").strip()
                    accused_index = int(accused_input) - 1 
                    play_sfx("click.wav")
                except Exception: 
                    type_text("Invalid selection format.") 
                    play_sfx("error.wav")
                    time.sleep(1)
                    continue

                if 0 <= accused_index < len(suspects):
                    accused = suspects[accused_index] 
                    
                    # REQUIREMENT CHECK: Do they have the proof for this specific suspect?
                    has_proof = True
                    if accused == "High Priest" and "ziggurat_foundation_lore" not in lexicon:
                        has_proof = False
                    elif accused == "Concubine" and "concept_of_the_floating_wood" not in lexicon:
                        has_proof = False
                    elif accused == "Bronze Smith" and "the_iron_heresy" not in lexicon:
                        has_proof = False

                    if not has_proof:
                        type_text(f"\nYou have no solid evidence linking the {accused} to the tide. The council dismisses your baseless claim.", color=COLOR_DANGER)
                        play_sfx("error.wav")
                        time.sleep(2)
                    elif accused == sea_thrall:
                        type_text("\nYOU GUESSED CORRECTLY. THE GUARDS DRAG THE THRALL TO THE ALTAR.", color=COLOR_SYSTEM)
                        play_sfx("victory.wav")
                        time.sleep(2) 
                        
                        clear_screen() 
                        type_text("THE SPY NETWORK IS BROKEN. THE ZIGGURAT PREPARES FOR WAR. YOU SURVIVED... FOR NOW.", color=COLOR_VICTORY)
                        save_lexicon([]) 
                        input("\n[Press Enter to return to the Compilation Menu]")
                        play_sfx("click.wav")
                        return 
                    else: 
                        type_text("\nWRONG. THE CITY GATES ARE LEFT UNGUARDED. THE TIDE RUSHES IN.", color=COLOR_DANGER)
                        play_sfx("game_over.wav")
                        time.sleep(2) 
                        days_remaining = 0 
                else:
                    type_text("Invalid suspect selection index.")
                    play_sfx("error.wav")
                    time.sleep(1)
            elif choice == "3": 
                current_location = "The Slums" 

        if terror >= 100:
            type_text("\nTHE WEIGHT OF THIS UNNATURAL KNOWLEDGE CRUSHES YOUR MIND. YOU COLLAPSE SCREAMING.", color=COLOR_DANGER)
            play_sfx("game_over.wav")
            time.sleep(3)
            days_remaining = 0

    clear_screen() 
    type_text("THE SEA SWALLOWS THE CIVILIZATION, BUT THE KNOWLEDGE OF FAILURE REMAINS.", color=COLOR_ABYSS, speed=0.05)
    print("\n") 
    input("[Press Enter to return to the Compilation Menu]")
    play_sfx("click.wav")

# --- GAME 2: THE EMPTIED FORM ---
def slow_print(text, speed=0.04, pause_at_end=0.5):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()
    time.sleep(pause_at_end)

def glitch_print(text):
    for char in text:
        if random.random() < 0.15:
            sys.stdout.write(random.choice(['#', '@', '%', '&', '?', 'X']))
        else:
            sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.08)
    print()
    time.sleep(1)

def leave_message():
    try:
        desktop_path = os.path.expanduser("~/Desktop/DO_NOT_RETURN.txt")
        with open(desktop_path, "w") as file:
            file.write("The halls are empty. There's nothing left for you.\n")
            file.write("Was there ever a game here?\n")
    except Exception:
        pass 

def show_emptied_form_credits():
    play_audio_track("title_music.mp3")
    clear_screen()
    slow_print("--- C R E D I T S ---", 0.05)
    print("\nCreated for the 2026 Necronomi-Jam")
    print("Theme: Cosmic Horror")
    print("Genres: Metroidvania & Roguelite")
    print("\nDeveloper: Team MS-FF")
    print("\nSpecial Thanks: The beauty of emptiness.")
    input("\n[Press Enter to return]")
    play_sfx("click.wav")

def run_emptied_form():
    play_audio_track("ambience.mp3") 
    inventory = []
    rooms_visited = 0
    
    descriptions = [
        "Stone walls. Cold floor. No doors, just endless archways leading deeper.",
        "A sprawling banquet hall. The tables are set, but the food rotted to dust centuries ago.",
        "A winding corridor. You hear a footstep behind you. When you turn, there is nothing.",
        "An empty courtyard. The sky above is a featureless, suffocating flat grey.",
        "A small antechamber. The silence here is so heavy it rings in your ears.",
        "A grand library. The books on the shelves are completely blank.",
        "A narrow hall lined with mirrors. Your reflection seems to move a fraction of a second too late."
    ]
    
    clear_screen() 
    slow_print("You descend into the forgotten ruins.", 0.06)
    slow_print("These halls seem emptier than you remembered.", 0.06)
    slow_print("They told you there would be glory.", 0.06)
    time.sleep(1.5) 
    
    while True:
        rooms_visited += 1 
        clear_screen() 
        
        if rooms_visited % 6 == 0 and len(inventory) < 3:
            slow_print("Wait...", 0.1)
            slow_print("Have you been in this exact room before?", 0.08)
            time.sleep(1.5) 
            
            if "Pale Chalk" not in inventory:
                slow_print("You are trapped in a recursive hallway. The architecture defies logic.")
                slow_print("Without a way to anchor your path, you wander until you starve.")
                slow_print("\n[GAME OVER] - The geometry claims another.", 0.02)
                play_sfx("game_over.wav")
                leave_message() 
                time.sleep(2) 
                return 
            else:
                slow_print("You mark the wall with chalk. You regain your bearings, and a new path tears open.")
                play_sfx("clue_unlock.wav")
                time.sleep(1) 
        
        elif rooms_visited % 9 == 0 and len(inventory) < 3:
            slow_print("The path ahead plunges into absolute, suffocating darkness.", 0.05)
            
            if "Rusted Lantern" not in inventory:
                slow_print("You step into the dark. Something you cannot see brushes against your leg.", 0.08)
                time.sleep(1) 
                slow_print("You run. You slip. The dark swallows you.")
                slow_print("\n[GAME OVER] - Clouded by the darkness.", 0.02)
                play_sfx("game_over.wav")
                leave_message() 
                time.sleep(2) 
                return 
            else:
                slow_print("You raise your lantern high. Its weak, sickly light uncovers a new path.")
                play_sfx("clue_unlock.wav")
                time.sleep(1) 
        
        else:
            current_desc = descriptions[(rooms_visited - 1) % len(descriptions)]
            slow_print(current_desc, 0.02) 
            
            if rooms_visited == 3 and "Rusted Lantern" not in inventory:
                print("\n") 
                slow_print("Floating upon nothing, you found a lantern.", 0.05)
                inventory.append("Rusted Lantern") 
                play_sfx("clue_unlock.wav")
            elif rooms_visited == 5 and "Pale Chalk" not in inventory:
                print("\n") 
                slow_print("Clutched in the skeletal hand of something long dead, you find chalk.", 0.05)
                inventory.append("Pale Chalk") 
                play_sfx("clue_unlock.wav")
            elif rooms_visited == 12 and "Obsidian Sigil" not in inventory:
                print("\n") 
                slow_print("A pedestal holds a broken pendant. It hums with an empty frequency.", 0.05)
                inventory.append("Broken Pendant") 
                play_sfx("clue_unlock.wav")
            
            if len(inventory) == 3:
                clear_screen() 
                slow_print("You found all that you sought, and yet, none at all.", 0.06)
                slow_print("A sudden, overwhelming compulsion forces you to the center of the labyrinth.", 0.06)
                time.sleep(2) 
                clear_screen() 
                slow_print("There was never a monster here to slay.", 0.08)
                time.sleep(1) 
                slow_print("Your duty is complete.", 0.1)
                slow_print("Perhaps now, you can rest.", 0.12)
                print("\n") 
                glitch_print("T H E   W O R L D   I S   E M P T Y")
                play_sfx("victory.wav")
                leave_message() 
                time.sleep(2) 
                return
        
        print("\nWhat do you do?") 
        print("1. Go North") 
        print("2. Go South") 
        print("3. Go East") 
        print("4. Go West") 
        
        try:
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
        except Exception:
            choice = ""
        
        if random.random() < 0.15:
            clear_screen() 
            slow_print("You try to move, but the corridors seamlessly rotate around you.", 0.06)
            slow_print("Your sense of direction is slipping.", 0.08)
            play_sfx("terror_spike.wav")
            time.sleep(2) 

# --- MASTER COMPILATION LAUNCHER MENU ---
def main():
    while True:
        play_audio_track("title_music.mp3") 
        clear_screen() 
        print("======================================================")
        print("||               T E A M  M S - F F ' S             ||")
        print("||         N E C R O N O M I - J A M   2 0 2 6      ||")
        print("||              C O M P I L A T I O N               ||")
        print("||                                                  ||")
        print("======================================================")
        print("\nSelect a story to enter:\n")
        print("1. The Salt Tide")
        print("2. The Emptied Form")
        print("3. Credits")
        print("4. How to Play / Tutorial")
        print("5. Quit Compilation")
        
        try:
            choice = input("\n> ").strip() 
            play_sfx("click.wav")
        except Exception:
            choice = ""
        
        if choice == '1':
            run_salt_tide()
        elif choice == '2':
            run_emptied_form()
        elif choice == '3':
            show_emptied_form_credits()
        elif choice == '4':
            show_tutorial()
        elif choice == '5':
            clear_screen() 
            print("Was there a game here?")
            time.sleep(1.5) 
            sys.exit() 
        else:
            print("Invalid command.") 
            play_sfx("error.wav")
            time.sleep(1) 

if __name__ == "__main__":
    try:
        main() 
    except KeyboardInterrupt:
        clear_screen() 
        print("\nWell. There wasn't a game here.\n")
        sys.exit()
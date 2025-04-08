import pygame
import sys
import os
import subprocess  # For calling Ollama
import threading   # For asynchronous LLM call
import gc          # Optional garbage collection

pygame.init()

# Hide the mouse pointer for touch screens
pygame.mouse.set_visible(False)

# --- FULLSCREEN SETUP ---
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Interactive Hitchhiker's Guide")
# Always in full screen mode on the Pi touchscreen

# Define Colors
GREEN       = (154, 195, 102)
SALMON      = (255, 160, 122)
PINK        = (239, 92, 150)
PURPLE      = (148, 116, 166)
DARK_PURPLE = (103, 78, 167)
BLUE        = (111, 174, 227)
BABY_BLUE   = (137, 207, 240)  # For popup text
GREY        = (128, 128, 128)  # For buttons, scrollbar track, etc.
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)

# Colors for the 6 stacked items (for main buttons)
list_colors = [
    GREEN,       # FOREWORD
    SALMON,      # HITCHHIKING
    PINK,        # MAPS
    PURPLE,      # GUIDES
    DARK_PURPLE, # USELESS INFO
    BLUE,        # DON'T PANIC
]

# Mapping main list button text to folder names.
main_to_folder = {
    "FOREWORD": "forward",
    "HITCHHIKING": "hitchhiking",
    "MAPS": "maps",
    "GUIDES": "guides",
    "USELESS INFO": "useless_info",
    "DON'T PANIC": "dont_panic"
}

# Position main buttons so they extend off-screen to the left
MAIN_BUTTON_X = -100
MAIN_BUTTON_WIDTH = 500  # width for main list buttons

# Calculate main list vertical positions:
num_buttons = 6
button_height = 20
bottom_margin = 96  # ~1 inch from bottom
bottom_button_y = HEIGHT - bottom_margin - button_height
top_button_y = bottom_button_y - (num_buttons - 1) * button_height

# Define the main list of buttons
buttons = [
    {"text": "FOREWORD",     "color": list_colors[0],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 0 * button_height, MAIN_BUTTON_WIDTH, button_height)},
    {"text": "HITCHHIKING",  "color": list_colors[1],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 1 * button_height, MAIN_BUTTON_WIDTH, button_height)},
    {"text": "MAPS",         "color": list_colors[2],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 2 * button_height, MAIN_BUTTON_WIDTH, button_height)},
    {"text": "GUIDES",       "color": list_colors[3],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 3 * button_height, MAIN_BUTTON_WIDTH, button_height)},
    {"text": "USELESS INFO", "color": list_colors[4],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 4 * button_height, MAIN_BUTTON_WIDTH, button_height)},
    {"text": "DON'T PANIC",  "color": list_colors[5],
     "rect": pygame.Rect(MAIN_BUTTON_X, top_button_y + 5 * button_height, MAIN_BUTTON_WIDTH, button_height)},
]

# Fonts
font_main = pygame.font.SysFont("Arial", 16, bold=True)
font_anim = pygame.font.SysFont("Arial", 16, bold=True)
font_popup = pygame.font.Font("assets/fonts/Orbitron-Regular.ttf", 16)
font_close = pygame.font.Font("assets/fonts/Orbitron-Regular.ttf", 20)
# New font for arrow buttons (using Arial, size 24, bold)
font_arrows = pygame.font.SysFont("Arial", 24, bold=True)

clock = pygame.time.Clock()

# --- QUIT BUTTON SETUP ---
QUIT_BUTTON_WIDTH = 80
QUIT_BUTTON_HEIGHT = 40
QUIT_BUTTON_RECT = pygame.Rect(WIDTH - QUIT_BUTTON_WIDTH - 10, 10, QUIT_BUTTON_WIDTH, QUIT_BUTTON_HEIGHT)

# --- GLOBAL VARIABLES FOR GUIDE MODE ---
guide_mode = False        # True when using the interactive LLM popup
llm_input_text = ""       # Text currently entered by the user
llm_conversation = []     # Conversation history (list of strings)
guide_scroll_offset = 0   # Scroll offset for the conversation area in guide mode

# Global list to track LLM threads
llm_threads = []

# --- Constants for scroll elements ---
SCROLLBAR_WIDTH = 6       # Narrow scroll bar width
SCROLL_BTN_WIDTH = 50     # Scroll arrow button width
SCROLL_BTN_HEIGHT = 50    # Scroll arrow button height

# --- BUILD PROMPT FUNCTION ---
def build_prompt(user_query):
    system_prompt = (
        "You are the Hitchhiker's Guide to the Galaxy. "
        "Respond in a quirky, dry, and witty style as if written by Douglas Adams. "
        "Keep your answers extremely short—only one or two sentences."
    )
    return system_prompt + "\n" + user_query

# --- HELPER FUNCTION: WORD WRAPPING ---
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# --- STREAMING LLM FUNCTION USING Ollama with tinyllama ---
def llm_thread_stream(prompt, response_index):
    try:
        process = subprocess.Popen(
            ["/usr/local/bin/ollama", "run", "tinyllama", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        accumulator = ""
        # Read output one character at a time.
        while True:
            char = process.stdout.read(1)
            if char == "" and process.poll() is not None:
                break
            if char:
                accumulator += char
                # Update conversation entry continuously.
                llm_conversation[response_index] = "Guide: " + accumulator
        process.stdout.close()
        process.wait()
    except Exception as e:
        llm_conversation[response_index] = "Guide: LLM Error: " + str(e)

# --- SPLASH SCREEN LOADING ANIMATION ---
original_splash = pygame.image.load("assets/images/dont-panic.png").convert_alpha()
splash_img = pygame.transform.smoothscale(original_splash,
                 (original_splash.get_width() // 2, original_splash.get_height() // 2))
splash_rect = splash_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
splash_duration = 3000  # 3 seconds
splash_start = pygame.time.get_ticks()

while pygame.time.get_ticks() - splash_start < splash_duration:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill(SALMON)
    screen.blit(splash_img, splash_rect)
    pygame.display.flip()
    clock.tick(60)
# --- END SPLASH SCREEN ---

# --- MAIN LIST ANIMATION SETUP ---
current_button_index = 0
main_list_animation_done = False
BUTTON_GROWTH_SPEED = 12
for button in buttons:
    button["rect"].width = 0
# --- END MAIN LIST ANIMATION SETUP ---

# Additional animation variables for expansion animation (generic for all buttons)
active_button = None
animate_expansion = False
retract_animation = False
intro_bar_width = 0
INTRO_BAR_MAX_WIDTH = 300
stack_bars_width = 0
STACK_BARS_MAX_WIDTH = 100
BAR_GROWTH_SPEED = 10
RETRACT_SPEED = 10
BAR_RETRACT_SPEED = 10
show_text = False

# Popup related variables (for file popup or LLM guide)
popup_active = False
popup_text = ""
popup_width = 700
popup_height = 500
SLIDE_SPEED = 10
popup_scroll_offset = 0

def draw_button(surface, button):
    pygame.draw.rect(surface, button["color"], button["rect"], border_radius=15)
    text_surf = font_main.render(button["text"], True, WHITE)
    text_rect = text_surf.get_rect(midright=(button["rect"].right - 10, button["rect"].centery))
    surface.blit(text_surf, text_rect)

def load_page_text(main_category, vertical_label):
    folder = main_to_folder.get(main_category, main_category.lower().replace(" ", "_"))
    file_path = os.path.join("assets", "pages", folder, f"{vertical_label.lower()}.txt")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return "Error loading content."
    return "Content not found."

running = True
while running:
    # --- MAIN LIST BUTTON ANIMATION ---
    if not main_list_animation_done:
        if current_button_index < len(buttons):
            btn = buttons[current_button_index]
            if btn["rect"].width < MAIN_BUTTON_WIDTH:
                btn["rect"].width += BUTTON_GROWTH_SPEED
            else:
                btn["rect"].width = MAIN_BUTTON_WIDTH
                current_button_index += 1
        else:
            main_list_animation_done = True

    click_pos = None
    handled_main_click = False

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if popup_active and guide_mode:
                if event.key == pygame.K_RETURN:
                    if llm_input_text.strip() != "":
                        prompt = build_prompt(llm_input_text)
                        llm_conversation.append("You: " + llm_input_text)
                        llm_conversation.append("Guide: ")
                        response_index = len(llm_conversation) - 1
                        t = threading.Thread(target=llm_thread_stream, args=(prompt, response_index))
                        t.daemon = True
                        t.start()
                        llm_threads.append(t)
                        llm_input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    llm_input_text = llm_input_text[:-1]
                else:
                    llm_input_text += event.unicode

        elif event.type == pygame.FINGERMOTION:
            if popup_active and guide_mode:
                SCROLL_FACTOR = 300
                guide_scroll_offset -= event.dy * SCROLL_FACTOR

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if QUIT_BUTTON_RECT.collidepoint(event.pos):
                running = False
                break

            if popup_active:
                popup_rect = pygame.Rect((WIDTH - popup_width) // 2, (HEIGHT - popup_height) // 2, popup_width, popup_height)
                close_button_rect = pygame.Rect(popup_rect.right - 40, popup_rect.top + 10, 30, 30)
                if event.button == 1 and close_button_rect.collidepoint(event.pos):
                    llm_threads.clear()
                    llm_conversation = []
                    llm_input_text = ""
                    popup_active = False
                    guide_mode = False
                    active_button = None
                    animate_expansion = False
                    retract_animation = False
                    intro_bar_width = 0
                    stack_bars_width = 0
                    show_text = False
                    popup_scroll_offset = 0
                    guide_scroll_offset = 0
                    gc.collect()

            if popup_active and guide_mode:
                margin = 20
                input_box_height = 40
                popup_rect = pygame.Rect((WIDTH - popup_width) // 2, (HEIGHT - popup_height) // 2, popup_width, popup_height)
                conversation_area_rect = pygame.Rect(
                    popup_rect.left + margin,
                    popup_rect.top + margin,
                    popup_rect.width - 2 * margin - (SCROLLBAR_WIDTH + SCROLL_BTN_WIDTH + 10),
                    popup_rect.height - 2 * margin - input_box_height - 10
                )
                # Place arrow buttons immediately to the right of the scrollbar.
                up_button_rect = pygame.Rect(
                    conversation_area_rect.right + 5,
                    conversation_area_rect.top + 60,  # Moved down by 60 pixels so it doesn't cover the X button
                    SCROLL_BTN_WIDTH, SCROLL_BTN_HEIGHT
                )
                down_button_rect = pygame.Rect(
                    conversation_area_rect.right + 5,
                    conversation_area_rect.bottom - SCROLL_BTN_HEIGHT,
                    SCROLL_BTN_WIDTH, SCROLL_BTN_HEIGHT
                )
                if event.button == 1:
                    if up_button_rect.collidepoint(event.pos):
                        guide_scroll_offset = max(guide_scroll_offset - 50, 0)
                    elif down_button_rect.collidepoint(event.pos):
                        guide_scroll_offset += 50

            if popup_active:
                if guide_mode:
                    if event.button == 4:
                        guide_scroll_offset -= 20
                    elif event.button == 5:
                        guide_scroll_offset += 20
                else:
                    if event.button == 4:
                        popup_scroll_offset -= 20
                    elif event.button == 5:
                        popup_scroll_offset += 20

            if not popup_active:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if active_button is not None and active_button == button and animate_expansion:
                            intro_bar_width = INTRO_BAR_MAX_WIDTH
                            stack_bars_width = STACK_BARS_MAX_WIDTH
                            show_text = True
                            animate_expansion = False
                        else:
                            active_button = button
                            animate_expansion = True
                            retract_animation = False
                            intro_bar_width = 0
                            stack_bars_width = 0
                            show_text = False
                        handled_main_click = True
                        break
                if not handled_main_click:
                    guide_button_width = MAIN_BUTTON_WIDTH - 250
                    guide_button_height = button_height
                    guide_button_x = MAIN_BUTTON_X
                    guide_button_y = HEIGHT - (bottom_margin / 1.75) - guide_button_height
                    guide_button_rect = pygame.Rect(guide_button_x, guide_button_y, guide_button_width, guide_button_height)
                    if guide_button_rect.collidepoint(event.pos):
                        popup_active = True
                        guide_mode = True
                        llm_input_text = ""
                        llm_conversation = []
                        guide_scroll_offset = 0
                        handled_main_click = True
                    else:
                        click_pos = event.pos

    if popup_active:
        for button in buttons:
            if button["rect"].x > -600:
                button["rect"].x -= SLIDE_SPEED
    else:
        for button in buttons:
            if button["rect"].x < MAIN_BUTTON_X:
                button["rect"].x += SLIDE_SPEED
                if button["rect"].x > MAIN_BUTTON_X:
                    button["rect"].x = MAIN_BUTTON_X

    screen.fill((250, 240, 120))

    for button in buttons:
        draw_button(screen, button)

    vertical_label_rects = []
    if active_button and not popup_active:
        active_button_rect = active_button["rect"]
        if retract_animation:
            show_text = False
            if stack_bars_width > 0:
                stack_bars_width -= BAR_RETRACT_SPEED
            elif intro_bar_width > 0:
                intro_bar_width -= RETRACT_SPEED
            else:
                animate_expansion = False
                active_button = None
        else:
            if animate_expansion:
                if intro_bar_width < INTRO_BAR_MAX_WIDTH:
                    intro_bar_width += BAR_GROWTH_SPEED
                elif stack_bars_width < STACK_BARS_MAX_WIDTH:
                    stack_bars_width += BAR_GROWTH_SPEED
                    show_text = True

        intro_rect = pygame.Rect(
            active_button_rect.right,
            active_button_rect.y,
            intro_bar_width,
            active_button_rect.height
        )
        pygame.draw.rect(screen, GREEN, intro_rect, border_radius=15)
        if show_text:
            intro_text_surf = font_anim.render("INTRODUCTION", True, WHITE)
            intro_text_rect = intro_text_surf.get_rect(midright=(intro_rect.right - 10, intro_rect.centery))
            screen.blit(intro_text_surf, intro_text_rect)

        if intro_bar_width >= INTRO_BAR_MAX_WIDTH and show_text:
            if active_button["text"] == "HITCHHIKING":
                labels = ["THE GUIDE"]
            else:
                labels = ["WHO", "WHAT", "WHY", "WHERE", "WHEN", "HOW"]
            bar_height = active_button_rect.height
            total_stack_height = len(labels) * bar_height
            bottom_anchor_y = intro_rect.top
            for i, label in enumerate(labels):
                topY = bottom_anchor_y - total_stack_height + i * bar_height
                bar_rect = pygame.Rect(
                    intro_rect.right - min(stack_bars_width, STACK_BARS_MAX_WIDTH),
                    topY,
                    min(stack_bars_width, STACK_BARS_MAX_WIDTH),
                    bar_height
                )
                pygame.draw.rect(screen, list_colors[i], bar_rect, border_radius=15)
                label_surf = font_anim.render(label, True, WHITE)
                label_rect = label_surf.get_rect(midright=(bar_rect.right - 10, bar_rect.centery))
                screen.blit(label_surf, label_rect)
                vertical_label_rects.append((label_rect, label))

    if not popup_active and click_pos is not None and vertical_label_rects and active_button:
        for rect, label in vertical_label_rects:
            if rect.collidepoint(click_pos):
                popup_text = load_page_text(active_button["text"], label)
                popup_active = True
                guide_mode = False
                active_button = None
                animate_expansion = False
                retract_animation = False
                intro_bar_width = 0
                stack_bars_width = 0
                show_text = False
                popup_scroll_offset = 0
                break

    purple_bar_height = 48
    purple_bar_rect = pygame.Rect(0, HEIGHT - purple_bar_height, WIDTH, purple_bar_height)
    pygame.draw.rect(screen, PURPLE, purple_bar_rect)

    guide_button_width = MAIN_BUTTON_WIDTH - 250
    guide_button_height = button_height
    guide_button_x = MAIN_BUTTON_X
    guide_button_y = HEIGHT - (bottom_margin / 1.75) - guide_button_height
    guide_button_rect = pygame.Rect(guide_button_x, guide_button_y, guide_button_width, guide_button_height)
    pygame.draw.rect(screen, list_colors[5], guide_button_rect, border_radius=15)
    guide_text_surf = font_main.render("THE GUIDE", True, WHITE)
    guide_text_rect = guide_text_surf.get_rect(midright=(guide_button_rect.right - 10, guide_button_rect.centery))
    screen.blit(guide_text_surf, guide_text_rect)

    # --- POPUP WINDOW DRAWING ---
    if popup_active:
        popup_rect = pygame.Rect((WIDTH - popup_width) // 2, (HEIGHT - popup_height) // 2, popup_width, popup_height)
        popup_border_thickness = 12
        outer_rect = popup_rect.inflate(popup_border_thickness, popup_border_thickness)
        pygame.draw.rect(screen, (80, 80, 80), outer_rect, border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), outer_rect, 2, border_radius=15)
        pygame.draw.rect(screen, BLACK, popup_rect, border_radius=10)

        # Draw close button ("X") in the upper right corner.
        close_button_rect = pygame.Rect(popup_rect.right - 40, popup_rect.top + 10, 30, 30)
        pygame.draw.rect(screen, GREY, close_button_rect)
        x_text = font_close.render("X", True, WHITE)
        x_text_rect = x_text.get_rect(center=close_button_rect.center)
        screen.blit(x_text, x_text_rect)

        if guide_mode:
            margin = 20
            input_box_height = 40
            # Define conversation area with room for a narrow scrollbar and arrow buttons.
            conversation_area_rect = pygame.Rect(
                popup_rect.left + margin,
                popup_rect.top + margin,
                popup_rect.width - 2 * margin - (SCROLLBAR_WIDTH + SCROLL_BTN_WIDTH + 10),
                popup_rect.height - 2 * margin - input_box_height - 10
            )
            input_box_rect = pygame.Rect(
                popup_rect.left + margin,
                popup_rect.bottom - margin - input_box_height,
                popup_rect.width - 2 * margin,
                input_box_height
            )
            # Draw conversation area with scrolling.
            screen.set_clip(conversation_area_rect)
            y_offset = conversation_area_rect.top - guide_scroll_offset
            total_conv_height = 0
            conv_lines = []
            for line in llm_conversation:
                wrapped = wrap_text(line, font_popup, conversation_area_rect.width)
                for wline in wrapped:
                    conv_lines.append(wline)
                    total_conv_height += font_popup.get_height() + 5
            for wline in conv_lines:
                text_surface = font_popup.render(wline, True, BABY_BLUE)
                screen.blit(text_surface, (conversation_area_rect.left, y_offset))
                y_offset += text_surface.get_height() + 5
            screen.set_clip(None)
            max_guide_offset = max(0, total_conv_height - conversation_area_rect.height)
            # Auto scroll down.
            guide_scroll_offset = max_guide_offset
            # Draw narrow scrollbar to the right of conversation area.
            track_x = conversation_area_rect.right
            track_y = conversation_area_rect.top
            track_height = conversation_area_rect.height
            pygame.draw.rect(screen, GREY, (track_x, track_y, SCROLLBAR_WIDTH, track_height))
            if total_conv_height > conversation_area_rect.height:
                thumb_height = (conversation_area_rect.height / total_conv_height) * track_height
                thumb_y = track_y + (guide_scroll_offset / max_guide_offset) * (track_height - thumb_height) if max_guide_offset > 0 else track_y
                pygame.draw.rect(screen, (200, 200, 200), (track_x, thumb_y, SCROLLBAR_WIDTH, thumb_height))
            # Draw scroll arrow buttons immediately to the right of the scrollbar.
            up_button_rect = pygame.Rect(
                track_x + SCROLLBAR_WIDTH + 5,
                conversation_area_rect.top + 60,
                SCROLL_BTN_WIDTH, SCROLL_BTN_HEIGHT
            )
            down_button_rect = pygame.Rect(
                track_x + SCROLLBAR_WIDTH + 5,
                conversation_area_rect.bottom - SCROLL_BTN_HEIGHT,
                SCROLL_BTN_WIDTH, SCROLL_BTN_HEIGHT
            )
            pygame.draw.rect(screen, GREY, up_button_rect, border_radius=5)
            pygame.draw.rect(screen, GREY, down_button_rect, border_radius=5)
            up_text = font_arrows.render("↑", True, WHITE)
            down_text = font_arrows.render("↓", True, WHITE)
            up_text_rect = up_text.get_rect(center=up_button_rect.center)
            down_text_rect = down_text.get_rect(center=down_button_rect.center)
            screen.blit(up_text, up_text_rect)
            screen.blit(down_text, down_text_rect)
            # Draw input box.
            pygame.draw.rect(screen, WHITE, input_box_rect, 2)
            input_text_surf = font_popup.render("> " + llm_input_text, True, WHITE)
            screen.blit(input_text_surf, (input_box_rect.left + 5, input_box_rect.centery - input_text_surf.get_height() / 2))
        else:
            scrollbar_width = 10
            text_clip_rect = pygame.Rect(popup_rect.left, popup_rect.top, popup_rect.width - (scrollbar_width + 5), popup_rect.height)
            screen.set_clip(text_clip_rect)
            margin = 20
            track_top_offset = 30
            effective_width = popup_rect.width - 2 * margin - (scrollbar_width + 5)
            lines_raw = popup_text.splitlines()
            wrapped_lines = []
            for line in lines_raw:
                wrapped_lines.extend(wrap_text(line, font_popup, effective_width))
            line_height = font_popup.get_height() + 5
            visible_area = popup_rect.height - 2 * margin - track_top_offset
            total_text_height = line_height * len(wrapped_lines)
            max_scroll_offset = max(total_text_height - visible_area, 0)
            popup_scroll_offset = max(0, min(popup_scroll_offset, max_scroll_offset))
            y_offset = popup_rect.top + margin + track_top_offset - popup_scroll_offset
            for line in wrapped_lines:
                text_surface = font_popup.render(line, True, BABY_BLUE)
                screen.blit(text_surface, (popup_rect.left + margin, y_offset))
                y_offset += text_surface.get_height() + 5
            screen.set_clip(None)
            track_x = popup_rect.right - scrollbar_width - 5
            track_y = popup_rect.top + margin + track_top_offset
            track_height = visible_area
            pygame.draw.rect(screen, GREY, (track_x, track_y, scrollbar_width, track_height))
            if total_text_height > visible_area:
                thumb_height = (visible_area / total_text_height) * track_height
                thumb_y = track_y + (popup_scroll_offset / max_scroll_offset) * (track_height - thumb_height) if max_scroll_offset > 0 else track_y
            else:
                thumb_height = track_height
                thumb_y = track_y
            THUMB_COLOR = (200, 200, 200)
            pygame.draw.rect(screen, THUMB_COLOR, (track_x, thumb_y, scrollbar_width, thumb_height))

    pygame.draw.rect(screen, GREY, QUIT_BUTTON_RECT, border_radius=5)
    pygame.draw.rect(screen, WHITE, QUIT_BUTTON_RECT, 2, border_radius=5)
    quit_text = font_main.render("QUIT", True, WHITE)
    quit_text_rect = quit_text.get_rect(center=QUIT_BUTTON_RECT.center)
    screen.blit(quit_text, quit_text_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()


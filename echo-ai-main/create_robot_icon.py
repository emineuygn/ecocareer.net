from PIL import Image, ImageDraw
import os

def create_cute_robot():
    # Create a new image with a transparent background
    size = (200, 200)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Colors
    primary_color = (76, 91, 224)  # Blue
    secondary_color = (255, 255, 255)  # White
    accent_color = (255, 200, 100)  # Light orange
    
    # Draw robot head (circle)
    draw.ellipse([40, 40, 160, 160], fill=primary_color)
    
    # Draw eyes (cute circles)
    draw.ellipse([70, 80, 90, 100], fill=secondary_color)
    draw.ellipse([110, 80, 130, 100], fill=secondary_color)
    
    # Draw small pupils
    draw.ellipse([75, 85, 85, 95], fill=accent_color)
    draw.ellipse([115, 85, 125, 95], fill=accent_color)
    
    # Draw cute smile
    draw.arc([80, 100, 120, 130], 0, 180, fill=secondary_color, width=3)
    
    # Draw antenna
    draw.rectangle([95, 20, 105, 40], fill=primary_color)
    draw.ellipse([90, 10, 110, 30], fill=accent_color)
    
    return image

def create_logo():
    # Create the logo
    logo = create_cute_robot()
    
    # Save the logo
    if not os.path.exists('assets'):
        os.makedirs('assets')
    logo.save('assets/logo.png', 'PNG')

def create_avatars():
    # Create user and bot avatars
    user_avatar = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    bot_avatar = create_cute_robot()
    bot_avatar = bot_avatar.resize((100, 100))
    
    # Save avatars
    if not os.path.exists('assets'):
        os.makedirs('assets')
    user_avatar.save('assets/user.png', 'PNG')
    bot_avatar.save('assets/bot.png', 'PNG')
    
    # Create additional icons
    send_icon = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(send_icon)
    draw.polygon([(10, 25), (40, 25), (25, 40)], fill=(255, 255, 255))
    send_icon.save('assets/send.png', 'PNG')
    
    back_icon = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(back_icon)
    draw.polygon([(30, 10), (10, 25), (30, 40)], fill=(255, 255, 255))
    back_icon.save('assets/back.png', 'PNG')
    
    # Create coin icon
    coin_icon = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(coin_icon)
    draw.ellipse([10, 10, 90, 90], fill=(255, 200, 50))
    draw.ellipse([20, 20, 80, 80], fill=(255, 180, 0))
    coin_icon.save('assets/coin.png', 'PNG') 
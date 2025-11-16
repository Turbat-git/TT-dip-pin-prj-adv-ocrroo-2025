import cv2
import numpy as np
import time

# Dictionary to store frames with their frame numbers
frames_storage = {}
frame_count = 0

def get_frame_rgb_array(frame_number):
    """
    Returns all RGB values present in a specific frame.
    
    Parameters:
    frame_number (int): The frame number to retrieve
    
    Returns:
    dict: Dictionary containing all RGB information from the frame
    """
    if frame_number not in frames_storage:
        print(f"Frame {frame_number} not found in storage")
        return None
    
    frame = frames_storage[frame_number]
    height, width, _ = frame.shape
    
    # Reshape frame to get all pixels as RGB values
    # OpenCV uses BGR, so we need to convert to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Reshape to get list of all RGB pixels
    all_pixels = frame_rgb.reshape(-1, 3)
    
    # Get unique colors and their counts
    unique_colors = {}
    for pixel in all_pixels:
        color_tuple = tuple(pixel)
        if color_tuple in unique_colors:
            unique_colors[color_tuple] += 1
        else:
            unique_colors[color_tuple] = 1
    
    # Sort by frequency (most common first)
    sorted_colors = sorted(unique_colors.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'frame_number': frame_number,
        'total_pixels': len(all_pixels),
        'unique_colors_count': len(unique_colors),
        'all_rgb_values': all_pixels,  # All RGB values as numpy array
        'unique_colors': sorted_colors,  # List of ((R,G,B), count) tuples
        'top_10_colors': sorted_colors[:10],  # Top 10 most frequent colors
        'frame_shape': frame.shape
    }

def analyze_frame_colors(frame_number, show_top_n=10):
    """
    Analyzes and displays color information for a specific frame.
    
    Parameters:
    frame_number (int): The frame number to analyze
    show_top_n (int): Number of top colors to display
    """
    data = get_frame_rgb_array(frame_number)
    
    if data is None:
        return
    
    print(f"\n{'='*60}")
    print(f"Frame {frame_number} Color Analysis")
    print(f"{'='*60}")
    print(f"Frame dimensions: {data['frame_shape'][0]}x{data['frame_shape'][1]}")
    print(f"Total pixels: {data['total_pixels']}")
    print(f"Unique colors found: {data['unique_colors_count']}")
    print(f"\nTop {show_top_n} most frequent colors:")
    print(f"{'Rank':<6} {'RGB Values':<20} {'Count':<10} {'Percentage'}")
    print(f"{'-'*60}")
    
    for i, ((r, g, b), count) in enumerate(data['top_10_colors'][:show_top_n], 1):
        percentage = (count / data['total_pixels']) * 100
        print(f"{i:<6} ({r:3d}, {g:3d}, {b:3d}){'':<7} {count:<10} {percentage:.2f}%")
    
    print(f"\nAll RGB values array shape: {data['all_rgb_values'].shape}")
    print(f"First 10 RGB values from frame:")
    for i, (r, g, b) in enumerate(data['all_rgb_values'][:10], 1):
        print(f"  Pixel {i}: RGB({r}, {g}, {b})")
    
    return data

# Main program
print("="*60)
print("10 SECOND VIDEO RECORDER - RGB FRAME ANALYZER")
print("="*60)
print("\nInitializing webcam...")

# taking the input from webcam
vid = cv2.VideoCapture(0)

if not vid.isOpened():
    print("Error: Could not open webcam")
    exit()

print("Webcam opened successfully!")
print("\nRecording will start in 3 seconds...")
time.sleep(1)
print("3...")
time.sleep(1)
print("2...")
time.sleep(1)
print("1...")
time.sleep(1)
print("\n🔴 RECORDING STARTED - 10 seconds\n")

# Record start time
start_time = time.time()
recording_duration = 10  # seconds

# Recording loop
while True:
    # capturing the current frame
    ret, frame = vid.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
    # Store the current frame
    frames_storage[frame_count] = frame.copy()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    remaining_time = recording_duration - elapsed_time
    
    # Display the current frame with timer
    display_frame = frame.copy()
    cv2.putText(display_frame, f"Recording: {remaining_time:.1f}s", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(display_frame, f"Frame: {frame_count}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Recording", display_frame)
    
    frame_count += 1
    
    # Check if 10 seconds have passed
    if elapsed_time >= recording_duration:
        print(f"⏹️  RECORDING STOPPED - {recording_duration} seconds completed")
        break
    
    # Small delay to allow window updates
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Recording interrupted by user")
        break

# releasing the video capture object and closing all windows
vid.release()
cv2.destroyAllWindows()

print(f"\n{'='*60}")
print(f"RECORDING COMPLETE")
print(f"{'='*60}")
print(f"Total frames captured: {frame_count}")
print(f"Recording duration: {elapsed_time:.2f} seconds")
print(f"Average FPS: {frame_count/elapsed_time:.2f}")
print(f"{'='*60}\n")

# User input loop
while True:
    try:
        user_input = input(f"\nEnter a frame number (0 to {frame_count-1}) to analyze, or 'q' to quit: ")
        
        if user_input.lower() == 'q':
            print("\nExiting program. Goodbye!")
            break
        
        frame_number = int(user_input)
        
        if frame_number < 0 or frame_number >= frame_count:
            print(f"❌ Invalid frame number. Please enter a number between 0 and {frame_count-1}")
            continue
        
        # Analyze the selected frame
        print(f"\nAnalyzing frame {frame_number}...")
        data = analyze_frame_colors(frame_number, show_top_n=15)
        
        # Ask if user wants to see all unique colors
        see_all = input(f"\nDo you want to see ALL {data['unique_colors_count']} unique colors? (y/n): ")
        if see_all.lower() == 'y':
            print(f"\nAll unique RGB colors in frame {frame_number}:")
            print(f"{'RGB Values':<20} {'Count':<10} {'Percentage'}")
            print(f"{'-'*50}")
            for (r, g, b), count in data['unique_colors']:
                percentage = (count / data['total_pixels']) * 100
                print(f"({r:3d}, {g:3d}, {b:3d}){'':<7} {count:<10} {percentage:.4f}%")
        
    except ValueError:
        print("❌ Invalid input. Please enter a valid frame number or 'q' to quit.")
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
        break

print("\nProgram ended.")
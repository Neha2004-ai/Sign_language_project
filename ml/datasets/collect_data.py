"""
ISL Real Data Collector — Webcam-Based Hand Landmark Recording.

Uses MediaPipe Hands to detect hand landmarks in real-time from your webcam,
then saves 21-point landmark data (x, y, z) as JSON files for each ISL sign.

Usage:
    python ml/datasets/collect_data.py

    # Collect specific signs only:
    python ml/datasets/collect_data.py --signs HELLO YES NO NAMASTE

    # Change number of samples per sign:
    python ml/datasets/collect_data.py --samples 50

Output:
    dataset/raw/<SIGN_NAME>/sample_001.json
    dataset/raw/<SIGN_NAME>/sample_002.json
    ...
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

import cv2
import numpy as np
import mediapipe as mp

# ISL signs organized by hand requirement
ONE_HAND_SIGNS = [
    "HELLO", "THANK YOU", "YES", "NO", "SORRY", "PLEASE", "WATER",
    "I LOVE YOU", "OK", "1", "2", "3", "4", "5"
]

TWO_HAND_SIGNS = [
    "NAMASTE", "HELP", "BOOK", "HOUSE", "TIME", "STOP", "WORK", "PEACE"
]

ALL_SIGNS = ONE_HAND_SIGNS + TWO_HAND_SIGNS

# Sign descriptions for on-screen guidance
SIGN_INSTRUCTIONS = {
    "HELLO": "Open hand, all 5 fingers spread, wave gently side to side",
    "THANK YOU": "Flat hand touches chin/lips, then moves forward and down",
    "YES": "Closed fist, thumb up, nod hand up and down",
    "NO": "Index + middle fingers snap together onto thumb",
    "SORRY": "Closed fist, rub in a circle on your chest",
    "PLEASE": "Flat palm, rub in a circle on your chest",
    "WATER": "W-hand (3 fingers) or thumb tilted toward mouth (drinking)",
    "I LOVE YOU": "Thumb + index + pinky extended, middle + ring curled",
    "OK": "Thumb and index tips touch (circle), other 3 fingers extended",
    "1": "Only index finger extended vertically",
    "2": "Index + middle finger extended (V-shape)",
    "3": "Thumb + index + middle extended",
    "4": "Four fingers extended (not thumb)",
    "5": "All five fingers extended and spread",
    "NAMASTE": "Both palms pressed together in front of chest (prayer position)",
    "HELP": "One flat palm facing up, other hand as fist placed on top, lift up",
    "BOOK": "Both flat palms together, then open outward like a book",
    "HOUSE": "Both hands fingertips touching at an angle forming a roof",
    "TIME": "Index finger taps the opposite wrist (like pointing at a watch)",
    "STOP": "One flat palm horizontal, other open hand descends onto it",
    "WORK": "Both hands in fists, tap wrists together",
    "PEACE": "Both hands showing V-sign (index + middle) spread apart"
}


def get_hand_type(sign_name: str) -> str:
    """Returns 'one_hand' or 'two_hand' based on the sign."""
    return "two_hand" if sign_name in TWO_HAND_SIGNS else "one_hand"


def landmarks_to_list(hand_landmarks) -> list:
    """Converts MediaPipe hand landmarks to a list of [x, y, z] coordinates."""
    return [
        {"x": round(lm.x, 6), "y": round(lm.y, 6), "z": round(lm.z, 6)}
        for lm in hand_landmarks.landmark
    ]


def collect_sign_data(
    sign_name: str,
    output_dir: str,
    num_samples: int = 30,
    countdown_seconds: int = 3,
    hold_seconds: float = 1.5
):
    """
    Collects real hand landmark data for a single ISL sign via webcam.

    Args:
        sign_name: Name of the ISL sign to collect.
        output_dir: Root output directory (e.g., 'dataset/raw').
        num_samples: Number of samples to record for this sign.
        countdown_seconds: Countdown before recording starts.
        hold_seconds: How long to hold the sign per sample.
    """
    sign_dir = os.path.join(output_dir, sign_name.replace(" ", "_"))
    os.makedirs(sign_dir, exist_ok=True)

    # Count existing samples to avoid overwriting
    existing = len([f for f in os.listdir(sign_dir) if f.endswith(".json")])

    hand_type = get_hand_type(sign_name)
    instruction = SIGN_INSTRUCTIONS.get(sign_name, "Perform the sign clearly in front of the camera")

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"ERROR: Cannot open webcam!")
        return 0

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    collected = 0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2 if hand_type == "two_hand" else 1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5
    ) as hands:

        print(f"\n{'='*60}")
        print(f"  Sign: {sign_name} ({hand_type})")
        print(f"  Instruction: {instruction}")
        print(f"  Samples to collect: {num_samples}")
        print(f"{'='*60}")
        print(f"  Press SPACE to start recording a sample")
        print(f"  Press 'S' to skip this sign")
        print(f"  Press 'Q' to quit entirely")
        print(f"{'='*60}\n")

        state = "WAITING"  # WAITING -> COUNTDOWN -> RECORDING -> SAVED
        countdown_start = 0
        record_start = 0

        while collected < num_samples:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Draw landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            # UI overlay
            overlay = frame.copy()

            # Top bar
            cv2.rectangle(overlay, (0, 0), (640, 70), (30, 30, 30), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

            cv2.putText(frame, f"Sign: {sign_name}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2)
            cv2.putText(frame, f"Sample: {collected + existing + 1}/{num_samples + existing} | Type: {hand_type}",
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # Bottom instruction bar
            cv2.rectangle(frame, (0, 420), (640, 480), (30, 30, 30), -1)

            if state == "WAITING":
                cv2.putText(frame, f"Instruction: {instruction[:70]}", (10, 445),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 255), 1)
                cv2.putText(frame, "Press SPACE to record | S to skip | Q to quit", (10, 465),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)

            elif state == "COUNTDOWN":
                elapsed = time.time() - countdown_start
                remaining = countdown_seconds - int(elapsed)
                if remaining <= 0:
                    state = "RECORDING"
                    record_start = time.time()
                else:
                    # Big countdown number
                    cv2.putText(frame, str(remaining), (280, 280),
                                cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 255, 255), 8)
                    cv2.putText(frame, "Get ready! Hold the sign...", (150, 450),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            elif state == "RECORDING":
                elapsed = time.time() - record_start
                if elapsed >= hold_seconds:
                    # Capture the sample
                    if results.multi_hand_landmarks and results.multi_handedness:
                        left_lms = None
                        right_lms = None

                        for idx, hand_info in enumerate(results.multi_handedness):
                            label = hand_info.classification[0].label
                            lms = landmarks_to_list(results.multi_hand_landmarks[idx])

                            # MediaPipe labels are mirrored when using front camera
                            if label == "Left":
                                right_lms = lms  # Mirrored: MP "Left" = user's Right
                            else:
                                left_lms = lms   # Mirrored: MP "Right" = user's Left

                        # Validate: for two_hand signs, we need both hands
                        hands_detected = (1 if left_lms else 0) + (1 if right_lms else 0)

                        if hand_type == "two_hand" and hands_detected < 2:
                            cv2.putText(frame, "Need BOTH hands! Try again.", (100, 300),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            state = "WAITING"
                        elif hand_type == "one_hand" and hands_detected < 1:
                            cv2.putText(frame, "No hand detected! Try again.", (100, 300),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            state = "WAITING"
                        else:
                            # Save sample
                            sample_data = {
                                "sign_name": sign_name,
                                "hands": hand_type,
                                "left_landmarks": left_lms,
                                "right_landmarks": right_lms,
                                "num_hands_detected": hands_detected,
                                "timestamp": datetime.now().isoformat(),
                                "sample_index": collected + existing
                            }

                            sample_filename = f"sample_{collected + existing + 1:04d}.json"
                            sample_path = os.path.join(sign_dir, sample_filename)

                            with open(sample_path, "w") as f:
                                json.dump(sample_data, f, indent=2)

                            collected += 1
                            print(f"  ✓ Saved {sample_filename} for '{sign_name}' ({collected}/{num_samples})")
                            state = "WAITING"
                    else:
                        cv2.putText(frame, "No hand detected! Try again.", (100, 300),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        state = "WAITING"
                else:
                    # Recording progress bar
                    progress = elapsed / hold_seconds
                    bar_width = int(400 * progress)
                    cv2.rectangle(frame, (120, 350), (520, 380), (50, 50, 50), -1)
                    cv2.rectangle(frame, (120, 350), (120 + bar_width, 380), (0, 255, 0), -1)
                    cv2.putText(frame, "RECORDING - Hold steady!", (150, 340),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    # Red recording dot
                    cv2.circle(frame, (600, 30), 12, (0, 0, 255), -1)

            cv2.imshow("ISL Data Collector", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and state == "WAITING":
                state = "COUNTDOWN"
                countdown_start = time.time()
            elif key == ord('s') or key == ord('S'):
                print(f"  Skipping '{sign_name}'")
                break
            elif key == ord('q') or key == ord('Q'):
                print("  Quitting data collection.")
                cap.release()
                cv2.destroyAllWindows()
                return -1  # Signal to quit

    cap.release()
    cv2.destroyAllWindows()

    print(f"  Collected {collected} samples for '{sign_name}' (total: {collected + existing})")
    return collected


def main():
    parser = argparse.ArgumentParser(description="ISL Real Data Collector")
    parser.add_argument("--signs", nargs="*", default=None,
                        help="Specific signs to collect (e.g., HELLO YES NO). Default: all signs")
    parser.add_argument("--samples", type=int, default=30,
                        help="Number of samples per sign (default: 30)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output directory (default: dataset/raw)")
    parser.add_argument("--countdown", type=int, default=3,
                        help="Countdown seconds before recording (default: 3)")
    parser.add_argument("--hold", type=float, default=1.5,
                        help="Seconds to hold the sign while recording (default: 1.5)")
    args = parser.parse_args()

    # Resolve output directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    output_dir = args.output or os.path.join(project_root, "dataset", "raw")
    os.makedirs(output_dir, exist_ok=True)

    # Determine which signs to collect
    signs_to_collect = args.signs if args.signs else ALL_SIGNS

    # Validate sign names
    invalid_signs = [s for s in signs_to_collect if s not in ALL_SIGNS]
    if invalid_signs:
        print(f"WARNING: Unknown signs will be collected as custom: {invalid_signs}")

    print("\n" + "=" * 60)
    print("  ISL Real Data Collector")
    print("=" * 60)
    print(f"  Signs to collect: {len(signs_to_collect)}")
    print(f"  Samples per sign: {args.samples}")
    print(f"  Output directory:  {output_dir}")
    print(f"  Hold duration:     {args.hold}s")
    print("=" * 60)
    print("\n  The webcam will open for each sign.")
    print("  Follow the on-screen instructions to record samples.\n")

    total_collected = 0
    for sign in signs_to_collect:
        result = collect_sign_data(
            sign_name=sign,
            output_dir=output_dir,
            num_samples=args.samples,
            countdown_seconds=args.countdown,
            hold_seconds=args.hold
        )
        if result == -1:
            break
        total_collected += max(0, result)

    print(f"\n{'='*60}")
    print(f"  Data Collection Complete!")
    print(f"  Total samples collected: {total_collected}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}")
    print(f"\n  Next step: Run 'python ml/datasets/process_data.py' to extract features.\n")


if __name__ == "__main__":
    main()

# >> streamlit run file_name.py  

# Imports from Python libraries

import streamlit as st
import matplotlib.pyplot as plt

# Imports from app modules

from metrics import coverage_area, overlap_area, best_guard, worst_guard
from state import GameState
from rules import new_game, add_guard,remove_all_guards, remove_last_guard
from config import (
    BASELINE_GUARDS, 
    BASELINE_NUM_ROOMS, 
    BASELINE_OVERLAP, 
    MIN_GUARDS, 
    MIN_NUM_ROOMS, 
    MIN_OVERLAP, 
    MAX_GUARDS, 
    MAX_NUM_ROOMS, 
    MAX_OVERLAP
)

# ------------------------------
# Move to parameters.py
# ------------------------------

# ------------------------------
# Initialize session state 
# ------------------------------

if 'game' not in st.session_state:
    st.session_state.game = GameState(None, None, {
        "num_rooms": BASELINE_NUM_ROOMS,
        "max_guards": BASELINE_GUARDS,
        "min_overlap": BASELINE_OVERLAP,
        "blind": False,
    })

game = st.session_state.game

# Application layout

st.title("Guarding an Art Gallery")

if game.floor_plan == None:

    st.write("""
        Welcome! Your task is to position a limited number of guards in an art gallery so that
        they can see as much of the gallery as possible. Guards can look around all 360 degrees, but they can't see
        through walls.
             
        When you're ready to play, click the button below.
        """)

    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        if st.button("Let's get started"):
            st.session_state.game = new_game(st.session_state.game.settings)
            st.rerun()

else:

    col11, col12 = st.columns([5, 1])

    # ------------------
    # Display floor plan
    # ------------------

    with col11:
                            
        fig, ax = plt.subplots()

        # Plot floor plan
        ax.plot(*game.floor_plan.exterior.xy, color="darkgray", linewidth=2)
        ax.grid(True, linestyle=':')

        # Plot guards
        if game.guards:
            for g in game.guards:

                if game.show_results():
                    # Plot visibility polygons
                    ax.fill(*g["visibility"].exterior.xy, color="red", alpha=0.5)

                ax.text(g["x"] + 0.1, g["y"] + 0.1, f"{g['id']}", color="black")
                
            gx = [g["x"] for g in game.guards]
            gy = [g["y"] for g in game.guards]
            ax.scatter(gx, gy, color="black", s=80, label="Guards")

        st.pyplot(fig)

    # --------------------------------
    # Dashboard of performance metrics
    #---------------------------------
        
    with col12:
        if game.show_results():
            st.metric(
                label="Covered by 1+", 
                value=f"{coverage_area(game):.0%}",
                help='Proportion of floor area observed by at least one guard'
            )
            st.metric(
                label="Covered by 2+", 
                value=f"{overlap_area(game):.0%}",
                help='Proportion of floor area observed by at least two guards'
            )
            st.metric(
                label="Most effective guard", 
                value=f"{best_guard(game):.0%}",
                help='Proportion of floor area observed by the guard who sees the most'
            )
            st.metric(
                label="Least effective guard", 
                value=f"{worst_guard(game):.0%}",
                help='Proportion of floor area observed by the guard who sees the least'
            )
        else:
            st.metric(
                label="Covered by 1+", 
                value="-",
                help='Proportion of floor area observed by at least one guard'
            )
            st.metric(
                label="Covered by 2+", 
                value="-",
                help='Proportion of floor area observed by at least two guards'
            )
            st.metric(
                label="Most effective guard", 
                value="-",
                help='Proportion of floor area observed by the guard who sees the most'
            )
            st.metric(
                label="Least effective guard", 
                value="-",
                help='Proportion of floor area observed by the guard who sees the least'
            )


    col21, col22 = st.columns([3, 3])
        
    # --------------------------
    # Form for adding new guards
    # --------------------------
        
    with col21:
        
        if game.floor_plan is not None:
            st.write("**Tools to move guards**")

            # --- Add a new guard ---
            if game.is_finished():
                st.info("Maximum number of guards reached!")
            else:
                # Set ranges for sliders
                x_min, y_min, x_max, y_max = game.floor_plan.bounds

                with st.form("new_guard_form"):
                    st.info(f"""
                        You can add up to {game.settings["max_guards"] - len(game.guards)} more guard(s). 
                        Use the sliders to set the position and then click the button to place the guard.
                        """)
                    x = st.slider("Horizontal coordinate", x_min, x_max, x_min)
                    y = st.slider("Vertical coordinate", y_min, y_max, y_min)

                    add = st.form_submit_button("Add guard")
                    if add:
                        try:
                            st.session_state.game = add_guard(st.session_state.game, x, y)
                            st.rerun()  # refresh UI to show updated game
                        except ValueError as e:
                            st.info(str(e))

            if game.guards:

                col22a, col22b = st.columns([3, 3])

                with col22a:

                    # Remove last guard
                    if st.button("Remove last guard"):
                        st.session_state.game = remove_last_guard(st.session_state.game)
                        st.rerun()

                with col22b:

                    # Remove all guards
                    if st.button("Remove all guards"):
                        st.session_state.game = remove_all_guards(st.session_state.game)
                        st.rerun()

    # -----------------------------------
    # Form for generating new floor plans
    # -----------------------------------

    with col22:
        st.write("**Tools for generating floor plans**")
                
        with st.form("new_settings_form"):
                    
            num_rooms = st.slider(
                "Number of rooms",
                MIN_NUM_ROOMS, MAX_NUM_ROOMS,
                game.settings["num_rooms"]
            )

            max_guards = st.slider(
                "Maximum number of guards",
                MIN_GUARDS, MAX_GUARDS,
                game.settings["max_guards"]
            )

            min_overlap = st.slider(
                "Minimum room overlap",
                MIN_OVERLAP, MAX_OVERLAP,
                game.settings["min_overlap"]
            )

            blind = st.toggle(
                "Play blind",
                value=game.settings["blind"],
                help="Hides visibility polygons and coverage metrics until the last guard in position"
            )

            submitted = st.form_submit_button("Start new game")

            if submitted:
                st.session_state.game.settings = {
                    "num_rooms": num_rooms,
                    "max_guards": max_guards,
                    "min_overlap": min_overlap,
                    "blind": blind,
                }
                st.session_state.game = new_game(st.session_state.game.settings) 
                st.rerun()



# Open folder in VS Code
# >> streamlit run file_name.py  

# Imports from Python libraries

import streamlit as st
import numpy as np 
import matplotlib.pyplot as plt
from shapely.geometry import Point, MultiPoint, LineString, Polygon, box, GeometryCollection

# Imports from app modules

from geometry import boundary_points, generate_floor_plan, visibility_polygon
from metrics import coverage_area, overlap_area, best_guard, worst_guard

# Specify game constants

MAX_GUARDS = 3
NUM_BDRY_PTS = 400
FLOOR_PLAN_BUFFER = 0.05
MIN_NUM_ROOMS = 3
MAX_NUM_ROOMS = 15
BASELINE_NUM_ROOMS = 5
MIN_OVERLAP = 0.01
BASELINE_OVERLAP = 0.10
MAX_OVERLAP = 0.20
D_OVERLAP = 0.01
MIN_GUARDS = 1
MAX_GUARDS = 10
BASELINE_GUARDS = 3
DX = 1
DY = 1

# Initialize session state 

if "pending_settings" not in st.session_state:
    st.session_state.pending_settings = {
        "num_rooms": BASELINE_NUM_ROOMS,
        "max_guards": BASELINE_GUARDS,
        "min_overlap": BASELINE_OVERLAP,
        "blind": False,
    }

if "active_settings" not in st.session_state:
    st.session_state.active_settings = {
        "num_rooms": BASELINE_NUM_ROOMS,
        "max_guards": BASELINE_GUARDS,
        "min_overlap": BASELINE_OVERLAP,
        "blind": False,
    }


if 'floor_plan' not in st.session_state:
    st.session_state.floor_plan = None
if 'bdry_pts' not in st.session_state:
    st.session_state.bdry_pts = None
if "guards" not in st.session_state:
    st.session_state.guards = []
if "next_guard_id" not in st.session_state:
    st.session_state.next_guard_id = 1

# Application layout

st.title("Guarding an Art Gallery")

if st.session_state.floor_plan == None:

    st.write("""
        Welcome! Your task is to position a limited number of guards in an art gallery so that
        they can see as much of the gallery as possible. Guards can look around all 360 degrees, but they can't see
        through walls.
             
        When you're ready to play, click the button below.
        """)

    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        if st.button("Let's get started"):
            st.session_state.guards = []
            st.session_state.next_guard_id = 1    
            st.session_state.floor_plan = generate_floor_plan(
                num_rooms=st.session_state.active_settings["num_rooms"],
                min_overlap=st.session_state.active_settings["min_overlap"],
                dx=DX,
                dy=DY
            )
            st.session_state.bdry_pts = boundary_points(st.session_state.floor_plan, FLOOR_PLAN_BUFFER, NUM_BDRY_PTS)  
            st.rerun()

else:

    col11, col12 = st.columns([5, 1])

    # --------------------
    # Prepare for this run
    # --------------------
        
    all_guards_in_place = len(st.session_state.guards) == st.session_state.active_settings["max_guards"]
    show_results = st.session_state.guards and (all_guards_in_place or not st.session_state.active_settings["blind"])

    # ------------------
    # Display floor plan
    # ------------------

    with col11:
                            
        fig, ax = plt.subplots()
        #ax.set_title("Art gallery's floor plan")

        # Plot floor plan
        ax.plot(*st.session_state.floor_plan.exterior.xy, color="darkgray", linewidth=2)
        ax.grid(True, linestyle=':')

        # Plot guards
        if st.session_state.guards:
            for g in st.session_state.guards:

                if show_results:
                    # Plot visibility polygons
                    ax.fill(*g["visibility"].exterior.xy, color="red", alpha=0.5)

                ax.text(g["x"] + 0.1, g["y"] + 0.1, f"{g['id']}", color="black")
                
            gx = [g["x"] for g in st.session_state.guards]
            gy = [g["y"] for g in st.session_state.guards]
            ax.scatter(gx, gy, color="black", s=80, label="Guards")

        st.pyplot(fig)

    # --------------------------------
    # Dashboard of performance metrics
    #---------------------------------
        
    with col12:
        if show_results:
            visibility_polygons = [g["visibility"] for g in st.session_state.guards]
            st.metric(
                label="Covered by 1+", 
                value=f"{coverage_area(st.session_state.floor_plan, visibility_polygons):.0%}",
                help='Proportion of floor area observed by at least one guard'
            )
            st.metric(
                label="Covered by 2+", 
                value=f"{overlap_area(st.session_state.floor_plan, visibility_polygons):.0%}",
                help='Proportion of floor area observed by at least two guards'
            )
            st.metric(
                label="Most effective guard", 
                value=f"{best_guard(st.session_state.floor_plan, visibility_polygons):.0%}",
                help='Proportion of floor area observed by the guard who sees the most'
            )
            st.metric(
                label="Least effective guard", 
                value=f"{worst_guard(st.session_state.floor_plan, visibility_polygons):.0%}",
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
        
        if st.session_state.floor_plan is not None:
            st.write("**Tools to move guards**")

            # --- Add a new guard ---
            max_guards = st.session_state.active_settings["max_guards"]

            if len(st.session_state.guards) < max_guards:
                # Set ranges for sliders
                x_min, y_min, x_max, y_max = st.session_state.floor_plan.bounds

                with st.form("new_guard_form"):
                    st.info(f"""
                        You can add up to {max_guards - len(st.session_state.guards)} more guard(s). 
                        Use the sliders to set the position and then click the button to place the guard.
                        """)
                    x = st.slider("Horizontal coordinate", x_min, x_max, x_min)
                    y = st.slider("Vertical coordinate", y_min, y_max, y_min)

                    add = st.form_submit_button("Add guard")
                    if add:
                        if st.session_state.floor_plan.contains(Point(x, y)):
                            vis_poly = visibility_polygon(Point(x, y), st.session_state.floor_plan, st.session_state.bdry_pts)
                            guard = {
                                "id": st.session_state.next_guard_id,
                                "x": x,
                                "y": y,
                                "visibility": vis_poly,
                            }
                            st.session_state.guards.append(guard)
                            st.session_state.next_guard_id += 1
                            st.rerun()  # refresh UI to show updated list
                        else:
                            st.info("The guard must be inside the art gallery. Try again with new coordinates.")

            else:
                st.info("Maximum number of guards reached!")

            if st.session_state.guards:

                col22a, col22b = st.columns([3, 3])

                with col22a:

                    # Remove last guard
                    if st.button("Remove last guard"):
                        st.session_state.guards.pop()
                        st.session_state.next_guard_id -= 1
                        st.rerun()

                with col22b:

                    # Remove all guards
                    if st.button("Remove all guards"):
                        st.session_state.guards = []
                        st.session_state.next_guard_id = 1
                        st.rerun()

        
    # -----------------------------------
    # Form for generating new floor plans
    # -----------------------------------

    with col22:
        st.write("**Tools for generating floor plans**")
                
        with st.form("new_settings_form"):
                    
            st.session_state.pending_settings["num_rooms"] = st.slider(
                "Number of rooms",
                MIN_NUM_ROOMS, MAX_NUM_ROOMS,
                st.session_state.pending_settings["num_rooms"]
            )

            st.session_state.pending_settings["max_guards"] = st.slider(
                "Maximum number of guards",
                MIN_GUARDS, MAX_GUARDS,
                st.session_state.pending_settings["max_guards"]
            )

            st.session_state.pending_settings["min_overlap"] = st.slider(
                "Minimum room overlap",
                MIN_OVERLAP, MAX_OVERLAP,
                st.session_state.pending_settings["min_overlap"]
            )

            st.session_state.pending_settings["blind"] = st.toggle(
                "Play blind",
                value=st.session_state.pending_settings["blind"],
                help="Hides visibility polygons and coverage metrics until the last guard in position"
            )

            submitted = st.form_submit_button("Start new game")

            if submitted:
                st.session_state.active_settings = st.session_state.pending_settings.copy()
                st.session_state.pending_settings = st.session_state.active_settings.copy()

                # reset game state based on active settings
                st.session_state.guards = []
                st.session_state.next_guard_id = 1    
                st.session_state.floor_plan = generate_floor_plan(
                    num_rooms=st.session_state.active_settings["num_rooms"],
                    min_overlap=st.session_state.active_settings["min_overlap"],
                    dx=DX,
                    dy=DY
                )
                st.session_state.bdry_pts = boundary_points(st.session_state.floor_plan, FLOOR_PLAN_BUFFER, NUM_BDRY_PTS)  
                st.rerun()





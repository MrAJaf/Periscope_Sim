import math
import streamlit as st
import matplotlib.pyplot as plt


# ---------- Geometry helpers ----------

def unit_vector_from_angle(deg):
    """Unit vector (x, y) for an angle in degrees from +x axis (CCW)."""
    rad = math.radians(deg)
    return math.cos(rad), math.sin(rad)


def reflect_vector(v, m):
    """
    Reflect direction vector v across a mirror whose direction is m (both tuples).
    m is a unit vector along the mirror surface.
    """
    vx, vy = v
    mx, my = m

    # a unit normal (perpendicular) to the mirror – either orientation works
    nx, ny = -my, mx
    dot = vx * nx + vy * ny
    rx = vx - 2 * dot * nx
    ry = vy - 2 * dot * ny

    length = math.hypot(rx, ry)
    if length == 0:
        return 0.0, 0.0
    return rx / length, ry / length


def intersect_ray_with_segment(p0, v, c, m, length):
    """
    Intersection of ray and finite mirror segment.

    p0: ray start (x, y)
    v : ray direction (unit vector)
    c : mirror centre (x, y)
    m : mirror direction (unit vector along mirror)
    length: total length of the mirror segment

    Returns (point, s, t) or None.
    """
    x0, y0 = p0
    vx, vy = v
    cx, cy = c
    mx, my = m

    bx = cx - x0
    by = cy - y0

    # Solve:
    # p0 + s*v = c + t*m  ->  s*v - t*m = c - p0
    D = -vx * my + mx * vy  # determinant
    if abs(D) < 1e-6:
        return None  # parallel / nearly parallel

    s = (bx * (-my) - (-mx) * by) / D
    t = (vx * by - vy * bx) / D

    if s < 0 or abs(t) > length / 2.0:
        return None

    ix = x0 + s * vx
    iy = y0 + s * vy
    return (ix, iy), s, t


# ---------- Drawing helpers ----------

def draw_periscope(ax):
    tube_left = 350
    tube_right = 450
    tube_bottom = 80
    tube_top = 520

    width = tube_right - tube_left
    height = tube_top - tube_bottom

    rect = plt.Rectangle(
        (tube_left, tube_bottom),
        width,
        height,
        fill=False,
        linewidth=2
    )
    ax.add_patch(rect)

    ax.text(400, 545, "Periscope (side view)",
            ha="center", va="bottom", fontsize=14, weight="bold")


def draw_mirror(ax, center, m, length, color="blue"):
    cx, cy = center
    half = length / 2.0
    mx, my = m

    x1 = cx - half * mx
    y1 = cy - half * my
    x2 = cx + half * mx
    y2 = cy + half * my

    ax.plot([x1, x2], [y1, y2], color=color, linewidth=4)


def draw_ray_path(ax, top_angle_deg, bottom_angle_deg, entry_height):
    mirror_length = 150

    # Mirror centres
    top_center = (400, 450)
    bottom_center = (400, 150)

    top_m = unit_vector_from_angle(top_angle_deg)
    bottom_m = unit_vector_from_angle(bottom_angle_deg)

    # Incoming ray from the left
    ray_start = (100, entry_height)
    ray_dir = (1.0, 0.0)

    # 1) To top mirror
    hit1 = intersect_ray_with_segment(ray_start, ray_dir,
                                      top_center, top_m, mirror_length)

    if hit1 is None:
        ax.plot(
            [ray_start[0], 750],
            [ray_start[1], ray_start[1]],
            color="red", linewidth=2
        )
        ax.text(220, entry_height + 10, "Incoming light", fontsize=10)
        return

    p1, _, _ = hit1
    ax.plot(
        [ray_start[0], p1[0]],
        [ray_start[1], p1[1]],
        color="red", linewidth=2
    )

    # Reflect from top mirror
    ray_dir = reflect_vector(ray_dir, top_m)

    # 2) To bottom mirror
    hit2 = intersect_ray_with_segment(p1, ray_dir,
                                      bottom_center, bottom_m, mirror_length)

    if hit2 is None:
        far = (p1[0] + ray_dir[0] * 1000, p1[1] + ray_dir[1] * 1000)
        ax.plot(
            [p1[0], far[0]],
            [p1[1], far[1]],
            color="red", linewidth=2
        )
        ax.text(220, entry_height + 10, "Incoming light", fontsize=10)
        return

    p2, _, _ = hit2
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color="red", linewidth=2
    )

    # Reflect from bottom mirror
    ray_dir = reflect_vector(ray_dir, bottom_m)

    # 3) Final outgoing ray
    far = (p2[0] + ray_dir[0] * 1000, p2[1] + ray_dir[1] * 1000)
    ax.plot(
        [p2[0], far[0]],
        [p2[1], far[1]],
        color="red", linewidth=2
    )

    ax.text(220, entry_height + 10, "Incoming light", fontsize=10)
    ax.text(560, 150, "Outgoing light", fontsize=10)


# ---------- Streamlit app ----------

def main():
    st.title("Periscope Light Ray Demonstrator")
    st.write(
        "Adjust the angles of the mirrors to see how the light ray "
        "reflects inside a simple periscope."
    )

    with st.sidebar:
        st.header("Controls")

        top_angle = st.slider(
            "Top mirror angle (° from +x axis, CCW)",
            min_value=90,
            max_value=170,
            value=135,
            step=1,
        )

        bottom_angle = st.slider(
            "Bottom mirror angle (° from +x axis, CCW)",
            min_value=-80,
            max_value=10,
            value=-45,
            step=1,
        )

        entry_height = st.slider(
            "Incoming ray height (y)",
            min_value=350,
            max_value=520,
            value=450,
            step=5,
        )

    fig, ax = plt.subplots(figsize=(8, 6))

    draw_periscope(ax)

    # Draw mirrors
    top_center = (400, 450)
    bottom_center = (400, 150)
    mirror_length = 150
    top_m = unit_vector_from_angle(top_angle)
    bottom_m = unit_vector_from_angle(bottom_angle)

    draw_mirror(ax, top_center, top_m, mirror_length, color="blue")
    draw_mirror(ax, bottom_center, bottom_m, mirror_length, color="blue")

    # Draw ray path
    draw_ray_path(ax, top_angle, bottom_angle, entry_height)

    # Axes formatting
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    st.pyplot(fig)


if __name__ == "__main__":
    main()

# 🐜 OptiAnt — Ant Colony Optimization Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with HTML](https://img.shields.io/badge/Made%20with-HTML%2FCSS%2FJS-orange)](https://developer.mozilla.org/en-US/)

**OptiAnt** is an interactive, web-based simulation that demonstrates the **Ant Colony Optimization (ACO)** metaheuristic in action. Inspired by the foraging behavior of real ants, this tool allows you to watch a virtual ant colony dynamically find the shortest path from their nest to food sources.

Unlike the classic Traveling Salesman Problem (TSP), OptiAnt models a **dynamic pathfinding problem**. You can actively modify the environment by placing obstacles (rocks, twigs) or adding new food sources (apples, sugar, mushrooms), forcing the colony to adapt and discover new optimal routes in real-time.

<p align="center">
  <!-- Add a screenshot of your game here! -->
  <!-- <img src="screenshot.png" alt="OptiAnt gameplay screenshot" width="800"> -->
</p>

## 🚀 Key Features

-   **🎮 Interactive Sandbox**: Use the side panel tools to place obstacles (🪨, 🪵), add new food sources (🍎, 🍬, 🍄), or erase objects by clicking directly on the map.
-   **🐜 Real-time ACO Simulation**: Watch artificial ants traverse the graph, leave pheromone trails, and collectively converge on the shortest path.
-   **⚙️ Adjustable Parameters**: Tweak the core ACO hyperparameters in real-time:
    -   `α (Alpha)`: Pheromone importance.
    -   `β (Beta)`: Heuristic distance importance.
    -   `ρ (Evaporation rate)`: How quickly pheromone trails fade.
    -   `Number of Ants`: Population size per iteration.
-   **📊 Visual Feedback**:
    -   Glowing pheromone trails (yellow) that intensify on shorter routes.
    -   A dashed "Best Path" overlay (purple) showing the current global optimum.
    -   Color-coded ants (blue for exploring, red for carrying food).
-   **💰 Build Points System**: Manage a resource pool (Build Points) to strategically place objects, adding a light game-strategy layer.

## 🧠 How It Works (The Algorithm)

The simulation strictly follows the **Ant-Cycle** model defined by Dorigo et al. (1996).

1.  **Graph Representation**: The environment is a fully connected graph where nodes represent the Nest and Food sources. Edges store distance and pheromone levels.
2.  **Solution Construction**: At each iteration, ants build a path from the Nest to a food source and back. They choose their next node using a **probabilistic transition rule**:
    \[
    p_{ij}^k = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}]^\beta}{\sum_{l \in allowed} [\tau_{il}]^\alpha \cdot [\eta_{il}]^\beta}
    \]
    Where \( \tau \) is the pheromone level and \( \eta = 1/distance \) is the heuristic visibility.
3.  **Pheromone Update**: Once all ants finish their tour:
    -   **Evaporation**: \( \tau_{ij} \leftarrow (1 - \rho) \cdot \tau_{ij} \) (prevents premature convergence).
    -   **Deposit**: Successful ants deposit pheromone proportionally to their tour quality: \( \Delta \tau_{ij}^k = Q / L_k \) (shorter paths receive more pheromone).
4.  **Dynamic Adaptation**: When you place a new food source or obstacle, the graph is rebuilt. The pheromone matrix resets, allowing the colony to "learn" the new environment from scratch—a standard practice in dynamic optimization scenarios.

## 🎮 How to Play

1.  **Run the Game**: Simply open the `index.html` file in your browser. No servers or installations are required!
2.  **Select a Tool**: Click a tool in the left panel (e.g., 🪨 Batu, 🍎 Apel).
3.  **Interact with the Map**: Click anywhere on the right-side canvas to place the selected object. Use the "Hapus" (Erase) tool to remove objects.
4.  **Control the Simulation**:
    -   **Mulai (Start)**: Begins the continuous simulation loop.
    -   **Pause**: Freezes the current state.
    -   **Step**: Runs a single iteration step-by-step.
    -   **Reset**: Clears all custom objects and restarts the simulation.

## 🖥️ Local Development & Setup

As this is a pure client-side application, getting started is as easy as 1-2-3:

```bash
# 1. Clone the repository
git clone https://github.com/americano-kr/OptiAnt.git

# 2. Navigate to the directory
cd optiant

# 3. Open the file (Mac/Linux/Windows)
open OptiAnt.html
# OR double-click the file in your file explorer.
```

## 📚 Theoretical References

This project is heavily inspired by foundational academic papers on Swarm Intelligence:

-   **Dorigo, M., Maniezzo, V., & Colorni, A. (1996).** *The Ant System: Optimization by a colony of cooperating agents.* IEEE Transactions on Systems, Man, and Cybernetics, Part B.
-   **Dorigo, M., & Stützle, T. (2004).** *Ant Colony Optimization.* MIT Press.
-   **Goss, S., Aron, S., Deneubourg, J. L., & Pasteels, J. M. (1989).** *Self-organized shortcuts in the Argentine ant.* Naturwissenschaften.

## 🛠️ Technologies Used

-   **HTML5**: Structure and semantic layout.
-   **CSS3**: Retro-styled UI with custom properties (CSS Variables) for easy theming.
-   **Vanilla JavaScript (ES6)**: All ACO logic, canvas rendering, and interaction handling is written from scratch using the Canvas API.

---

> **Note**: The UI language is currently set to **Indonesian**. Feel free to modify the text inside the HTML file to your preferred language.

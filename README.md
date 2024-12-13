# cs4756-Final-Project
visualization will not work with world.json right now since positions have not been added

## Model Game State Format
$$ T = \#\text{ of territories}$$

$T \times 2$ tensor:
$$\begin{bmatrix} o_1 & u_1 \\ o_2 & u_2 \\ \vdots & \vdots \\ o_T & u_T \end{bmatrix}$$

Where $o_i$ encodes the owner id of and $u_i$ encodes the number of units on territory $i$,  

## Model Player GetActions() Format
$$ T = \# \text{ of territories}, R = \text{reinforcement count}$$

$3 \times T \times T$ Tensor: $$\begin{bmatrix} \begin{bmatrix} R & \mathbf{0} \\ \mathbf{0} & \mathbf{0} \end{bmatrix} & \begin{bmatrix} a_{1,1} & a_{2,1} & \dots & a_{T,1} \\ \vdots & \vdots & \vdots & \vdots \\ a_{1,T} & a_{2,T} & \dots & a_{T,T} \end{bmatrix} & \begin{bmatrix} o_{1,1} & \dots & o_{T,1} \\ \vdots & & \vdots \\ o_{1,T} & \dots & o_{T,T} \end{bmatrix} \end{bmatrix}$$

Where  $R$ is the total number of accessible reinforcements (stored in position $(0,0)$), $a_{i,j}$ is $1$ if territories $i$ and $j$ are adjacent and 0 otherwise, and $o_{i,j}$ is the number of troops the player *could* move from $i$ to $j$. 

## Model Player Action Format

$3 \times T \times 2$ Tensor: $$\begin{bmatrix} \begin{bmatrix} r_1 & 0 \\ r_2 & 0 \\ \vdots & \vdots \\ r_T & 0\end{bmatrix} & \begin{bmatrix} a_1 & d_1 \\ a_2 & d_2 \\ \vdots & \vdots \\ a_T & d_T \end{bmatrix} & \begin{bmatrix} \vdots & \vdots \\ x & y \\ \vdots & \vdots \end{bmatrix} \end{bmatrix}$$

Where $r$ is the number of reinforcements to deploy to territory $i$, $a_i$  is the number of attacking troops to send at $d_i$ (keep sending until the number is reached), and $x$ indicates how many troops (from the territory at index $x$) to send to the territory at index $y$.

Since having multiple stages of actions severely complicates the process of learning a model, here the model assumes that they must decide what reinforcements, attacks, and fortifications to do *on the start of their turn*, fortifications then play out to the *extend possible*.
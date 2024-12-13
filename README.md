# cs4756-Final-Project
visualization will not work with world.json right now since positions have not been added

## Model Game State Format
$$ T = \#\text{ of territories}$$

$T \times 2$ tensor:
$$\begin{bmatrix} o_1 & u_1 \\ o_2 & u_2 \\ \vdots & \vdots \\ o_T & u_T \end{bmatrix}$$

Where $o_i$ encodes the owner id of and $u_i$ encodes the number of units on territory $i$,  

## New Format
$$\text{observation = } \begin{bmatrix}\begin{bmatrix} o_0 & u_0 \\ \vdots & \vdots \\ o_{T-1} & u_{T-1} \end{bmatrix}&R& A \end{bmatrix},$$
$$ \text{action = }\begin{bmatrix}\begin{bmatrix}r_0 \\ \vdots \\ r_{T-1}\end{bmatrix}\begin{bmatrix}a_{0,0} & \dots & a_{T-1,0} \\ \vdots & & \vdots \\ a_{0,T-1} & \dots & a_{T-1,T-1} \end{bmatrix} \begin{bmatrix} f_{0,0} & \dots & f_{T-1,0} \\ \vdots & & \vdots \\ f_{0,T-1} & \dots & f_{T-1,T-1} \end{bmatrix}\end{bmatrix}$$

$o$ values indicate whether the player is in control of a territory (if the indicator is the same as the current player ID), R is given by the environment as the total number of reinforcements. Can force the computer to fully commit to a reinforce if this still isn't working. $a$ values indicate along which *edge* to attack with how many troops. 0 all rows that are not controlled by the player. $A$ is adjacency. This gives an action space that is $T \times (2T + 1)$ and is integer valued and observation space that is $T \times (T+3)$ and also integer valued.

To 'clean' prediction output, can set all rows of the action matrix where $o_i \neq id$ to 0 since, no fortification, attack, or reinforcement can occur on a non-player controlled territory. Normalize the reinforcement values such that their sum is less than or equal to $R$, clamp the attack and fortify values (by row) such that the sub-sections of the rows are also normalized to $u_i$ for each $i$.

Network can thus be $f(x : T \times (3 + T)) = y : T \times (2T + 1)$
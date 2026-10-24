SimulationData::SimulationData()
{
 msections = LoadMenus();
 wtypes = LoadWalls();
 elements = GetElements();
 init_can_move();
}
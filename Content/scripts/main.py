import unreal
from neo4j import GraphDatabase

class MazePopulator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database="world")

    def close(self):
        self.driver.close()

    def create_cube(self, name, location, scale):
        # Load the cube asset
        actor_class = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
        # Ensure the actor class is valid
        if actor_class is None:
            raise RuntimeError('Failed to load cube asset.')

        # Set the actor location and scale
        actor_location = unreal.Vector(location[0], location[1], location[2])
        actor_scale = unreal.Vector(scale[0], scale[1], scale[2])

        # Spawn the cube in the level
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(actor_class, actor_location)
        actor.set_actor_scale3d(actor_scale)
        actor.set_actor_label(name)

    def populate_maze(self):
        with self.driver.session() as session:
            # Populate sectors
            sectors = session.run("MATCH (s:Sector) RETURN s")
            for record in sectors:
                sector = record["s"]
                if sector["center_x"] is not None and sector["center_y"] is not None:
                    self.create_cube(
                        f"Sector_{sector['name']}",
                        (sector["center_x"] * 100, sector["center_y"] * 100, 0),
                        (sector["width"], sector["height"], 100)
                    )
                else:
                    unreal.log_error(f"Sector {sector['name']} has invalid center coordinates.")

            # Populate arenas
            arenas = session.run("MATCH (a:Arena) RETURN a")
            for record in arenas:
                arena = record["a"]
                if arena["center_x"] is not None and arena["center_y"] is not None:
                    self.create_cube(
                        f"Arena_{arena['name']}",
                        (arena["center_x"] * 100, arena["center_y"] * 100, 100),
                        (arena["width"], arena["height"], 100)
                    )
                else:
                    unreal.log_error(f"Arena {arena['name']} has invalid center coordinates.")

            # Populate game objects
            game_objects = session.run("MATCH (g:GameObject) RETURN g")
            for record in game_objects:
                game_object = record["g"]
                if game_object["center_x"] is not None and game_object["center_y"] is not None:
                    self.create_cube(
                        f"GameObject_{game_object['name']}",
                        (game_object["center_x"] * 100, game_object["center_y"] * 100, 200),
                        (game_object["width"], game_object["height"], 100)
                    )
                else:
                    unreal.log_error(f"GameObject {game_object['name']} has invalid center coordinates.")

            # Populate spawning locations
            spawning_locations = session.run("MATCH (sl:SpawningLocation) RETURN sl")
            for record in spawning_locations:
                spawning_location = record["sl"]
                if spawning_location["center_x"] is not None and spawning_location["center_y"] is not None:
                    self.create_cube(
                        f"SpawningLocation_{spawning_location['name']}",
                        (spawning_location["center_x"] * 100, spawning_location["center_y"] * 100, 300),
                        (spawning_location["width"], spawning_location["height"], 100)
                    )
                else:
                    unreal.log_error(f"SpawningLocation {spawning_location['name']} has invalid center coordinates.")

# Usage example
maze_populator = MazePopulator("bolt://localhost:7687", "neo4j", "ABhijeet55")
maze_populator.populate_maze()
maze_populator.close()

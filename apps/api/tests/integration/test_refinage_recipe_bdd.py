from uuid import uuid4

from api.db.models import Item, Material, MaterialType, RefinageRecipe
from api.db.repositories import RefinageRecipeRepository
from api.services import RefinageRecipeService


async def _create_material(test_db_session, *, name: str, material_type_id):
    """Create an item and its material row for an integration recipe test."""

    item = Item(name=f"{name} {uuid4()}")
    test_db_session.add(item)
    await test_db_session.flush()
    material = Material(item_id=item.id, type=material_type_id)
    test_db_session.add(material)
    await test_db_session.flush()
    return material


async def test_bdd_recipe_service_returns_recipes_for_origin(test_db_session):
    """Return recipes for one origin without leaking recipes from another origin."""

    material_type = MaterialType(name=f"BDD recipe type {uuid4()}")
    test_db_session.add(material_type)
    await test_db_session.flush()
    origin = await _create_material(
        test_db_session,
        name="BDD recipe origin",
        material_type_id=material_type.id,
    )
    other_origin = await _create_material(
        test_db_session,
        name="BDD other recipe origin",
        material_type_id=material_type.id,
    )
    result_one = await _create_material(
        test_db_session,
        name="BDD recipe result one",
        material_type_id=material_type.id,
    )
    result_two = await _create_material(
        test_db_session,
        name="BDD recipe result two",
        material_type_id=material_type.id,
    )
    test_db_session.add_all(
        [
            RefinageRecipe(result=result_one.item_id, origin=origin.item_id, quantity=3),
            RefinageRecipe(result=result_two.item_id, origin=origin.item_id, quantity=8),
            RefinageRecipe(
                result=result_one.item_id,
                origin=other_origin.item_id,
                quantity=1,
            ),
        ]
    )
    await test_db_session.flush()

    recipes = await RefinageRecipeService(
        RefinageRecipeRepository(test_db_session)
    ).get_by_origin(origin.item_id)

    assert sorted((recipe.result, recipe.quantity) for recipe in recipes) == sorted([
        (result_one.item_id, 3),
        (result_two.item_id, 8),
    ])

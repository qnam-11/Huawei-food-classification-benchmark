import pytest

from app.services.knowledge_base import KnowledgeBase


def test_pho_values(kb):
    row = kb.get("pho")
    assert row["name_vi"] == "Phở"
    assert row["name_en"] == "Beef noodle soup"


def test_pho_nutrition_per_100g_and_serving(kb):
    block = kb.nutrition_for("pho")
    assert block["per_100g"] == {
        "kcal": 70,
        "protein_g": 4.5,
        "carb_g": 9.0,
        "fat_g": 1.8,
    }
    assert block["serving_g"] == 550
    assert block["per_serving"]["kcal"] == 385
    assert block["verified"] is False
    assert block["source"] == "draft_general_knowledge"


def test_bom_is_handled(kb):
    # a BOM would turn the first column into "\ufeffid"
    assert "id" not in kb.slugs
    assert "pho" in kb.slugs


def test_missing_macros_return_none(tmp_path):
    csv_path = tmp_path / "foods.csv"
    csv_path.write_text(
        "id,slug,name_vi,name_en,group,kcal_100g,protein_100g,carb_100g,fat_100g,"
        "serving_g,density_g_ml,shape,nutrition_source,source_id,verified\n"
        "0,pho,Phở,Beef noodle soup,dish,,,,,550,1.0,bowl,draft,,False\n",
        encoding="utf-8-sig",
    )
    block = KnowledgeBase(csv_path).nutrition_for("pho")
    assert block is None


def test_duplicate_slug_fails(tmp_path):
    csv_path = tmp_path / "foods.csv"
    csv_path.write_text(
        "id,slug,name_vi,name_en,group,kcal_100g,protein_100g,carb_100g,fat_100g,"
        "serving_g,density_g_ml,shape,nutrition_source,source_id,verified\n"
        "0,pho,Phở,Beef noodle soup,dish,70,4.5,9,1.8,550,1.0,bowl,draft,,False\n"
        "1,pho,Phở,Beef noodle soup,dish,70,4.5,9,1.8,550,1.0,bowl,draft,,False\n",
        encoding="utf-8-sig",
    )
    with pytest.raises(ValueError, match="duplicate slug"):
        KnowledgeBase(csv_path)


def test_bad_macro_fails_at_load(tmp_path):
    csv_path = tmp_path / "foods.csv"
    csv_path.write_text(
        "id,slug,name_vi,name_en,group,kcal_100g,protein_100g,carb_100g,fat_100g,"
        "serving_g,density_g_ml,shape,nutrition_source,source_id,verified\n"
        "0,pho,Phở,Beef noodle soup,dish,abc,4.5,9,1.8,550,1.0,bowl,draft,,False\n",
        encoding="utf-8-sig",
    )
    with pytest.raises(ValueError, match="pho"):
        KnowledgeBase(csv_path)


def test_non_finite_macro_fails_at_load(tmp_path):
    csv_path = tmp_path / "foods.csv"
    csv_path.write_text(
        "id,slug,name_vi,name_en,group,kcal_100g,protein_100g,carb_100g,fat_100g,"
        "serving_g,density_g_ml,shape,nutrition_source,source_id,verified\n"
        "0,pho,Phở,Beef noodle soup,dish,nan,4.5,9,1.8,550,1.0,bowl,draft,,False\n",
        encoding="utf-8-sig",
    )
    with pytest.raises(ValueError, match="finite"):
        KnowledgeBase(csv_path)

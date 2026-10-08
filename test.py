import file


def test_paris_est_couvert():
    couverture = file.calculer_couverture(2.3858, 48.8987)
    assert couverture["orange"] == {"2G": True, "3G": True, "4G": True}


def test_free_na_pas_de_2g():
    couverture = file.calculer_couverture(2.3858, 48.8987)
    assert couverture["free"]["2G"] is False


def test_en_pleine_mer_rien_nest_couvert():
    couverture = file.calculer_couverture(-8.0, 47.0)
    assert couverture["orange"] == {"2G": False, "3G": False, "4G": False}
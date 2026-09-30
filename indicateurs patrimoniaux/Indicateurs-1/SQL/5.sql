-- OGEP
SELECT ref_assainissement.ogep.identifiantogep,
	ref_assainissement.ogep.natureogep,
	ref_assainissement.ogep.longueur,
	ref_assainissement.ogep.domanialite,
	ref_assainissement.bvgrand.identifiantbvgrand,
	ref_assainissement.bvgrand.identifiantsteu,
	ref_assainissement.bvgrand.nomsteu,
	ref_cadastre.commune.id_com,
	ref_cadastre.commune.texte,
	ref_milieuxaquatiques.ruisseaubv.identifiantcoursdeau,
	ref_milieuxaquatiques.ruisseaubv.identifiantbassinversantruisseau,
	ref_assainissement.ogep.geom,
	captageperim.identifiantcaptage,
	captageperim.nomcaptage
FROM ref_assainissement.ogep
	LEFT JOIN ref_assainissement.bvgrand ON ST_Intersects(
		ST_Centroid(ref_assainissement.ogep.geom),
		ref_assainissement.bvgrand.geom
	)
	LEFT JOIN ref_cadastre.commune ON ST_Intersects(
		ST_Centroid(ref_assainissement.ogep.geom),
		ref_cadastre.commune.geom
	)
	LEFT JOIN ref_milieuxaquatiques.ruisseaubv ON ST_Intersects(
		ST_Centroid(ref_assainissement.ogep.geom),
		ref_milieuxaquatiques.ruisseaubv.geom
	)
	LEFT JOIN (
		WITH captage_e565 AS (
			SELECT ref_eaupotable.captageperim.identifiantcaptage,
				ref_eaupotable.captage.nomcaptage,
				ref_eaupotable.captageperim.geom
			FROM ref_eaupotable.captageperim
				INNER JOIN ref_eaupotable.captage ON ref_eaupotable.captageperim.identifiantcaptage = ref_eaupotable.captage.identifiantcaptage
			WHERE ref_eaupotable.captageperim.niveau = 'E'
				AND ref_eaupotable.captageperim.identifiantcaptage = 'E565'
		),
		autres_captages AS (
			SELECT ref_eaupotable.captageperim.identifiantcaptage,
				ref_eaupotable.captage.nomcaptage,
				ref_eaupotable.captageperim.geom,
				ST_Union(ref_eaupotable.captageperim.geom) OVER () AS geom_union
			FROM ref_eaupotable.captageperim
				INNER JOIN ref_eaupotable.captage ON ref_eaupotable.captageperim.identifiantcaptage = ref_eaupotable.captage.identifiantcaptage
			WHERE ref_eaupotable.captageperim.niveau = 'E'
				AND ref_eaupotable.captageperim.identifiantcaptage != 'E565'
		) -- Récupération du E565 découpé
		SELECT e565.identifiantcaptage,
			e565.nomcaptage,
			ST_Difference(e565.geom, autres.geom_union) AS geom
		FROM captage_e565 e565,
			(
				SELECT DISTINCT geom_union
				FROM autres_captages
			) autres
		UNION ALL
		-- Récupération de tous les autres polygones sans modification
		SELECT identifiantcaptage,
			nomcaptage,
			geom
		FROM autres_captages
	) AS captageperim ON ST_Intersects(
		ST_Centroid(ref_assainissement.ogep.geom),
		captageperim.geom
	)
where ref_assainissement.ogep.domanialite = 2;
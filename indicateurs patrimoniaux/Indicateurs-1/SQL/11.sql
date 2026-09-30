-- Traitement
WITH ranked_results AS (
	SELECT DISTINCT ref_assainissement.traitement.identifianttraitement,
		ref_assainissement.traitement.typetraitement,
		(
			DATE_PART(
				'year',
				ref_assainissement.traitement.datecreation
			) <= planrecol.anne_recol
		) AS recolement,
		ref_cadastre.commune.id_com,
		ref_cadastre.commune.texte,
		ref_assainissement.canap.typeadministratifreseau,
		ref_milieuxaquatiques.ruisseaubv.identifiantcoursdeau,
		ref_milieuxaquatiques.ruisseaubv.identifiantbassinversantruisseau,
		ref_assainissement.bvgrand.identifiantbvgrand,
		ref_assainissement.bvgrand.identifiantsteu,
		ref_assainissement.bvgrand.nomsteu,
		captageperim.identifiantcaptage,
		captageperim.nomcaptage,
		ROW_NUMBER() OVER (
			PARTITION BY ref_assainissement.traitement.identifianttraitement
			ORDER BY (
					DATE_PART(
						'year',
						ref_assainissement.traitement.datecreation
					) <= planrecol.anne_recol
				) DESC
		) AS rn,
		ref_assainissement.traitement.geom
	FROM ref_assainissement.traitement
		LEFT JOIN ref_assainissement.canap ON ST_Intersects(
			ref_assainissement.traitement.geom,
			ref_assainissement.canap.geom
		)
		LEFT JOIN ref_assainissement.bvgrand ON ST_Intersects(
			ST_Centroid(ref_assainissement.traitement.geom),
			ref_assainissement.bvgrand.geom
		)
		LEFT JOIN ref_cadastre.commune ON ST_Intersects(
			ST_Centroid(ref_assainissement.traitement.geom),
			ref_cadastre.commune.geom
		)
		LEFT JOIN ref_milieuxaquatiques.ruisseaubv ON ST_Intersects(
			ST_Centroid(ref_assainissement.traitement.geom),
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
			ST_Centroid(ref_assainissement.traitement.geom),
			captageperim.geom
		)
		LEFT JOIN (
			SELECT ref_assainissement.planrecol.identifiantplanrecol,
				ref_assainissement.planrecol.etatplanrecolement,
				EXTRACT(
					YEAR
					FROM ref_assainissement.planrecol.dateplanrecolement
				) as anne_recol,
				ref_assainissement.planrecol.geom
			FROM ref_assainissement.planrecol
			WHERE ref_assainissement.planrecol.etatplanrecolement = 'I'
		) AS planrecol ON ST_Intersects(
			ST_Centroid(ref_assainissement.traitement.geom),
			planrecol.geom
		)
	WHERE NOT EXISTS (
			SELECT 1
			FROM ref_assainissement.steu
			WHERE ST_Intersects(
					ref_assainissement.traitement.geom,
					ref_assainissement.steu.geom
				)
		)
		AND NOT EXISTS (
			SELECT 1
			FROM ref_assainissement.stare
			WHERE ST_Intersects(
					ref_assainissement.traitement.geom,
					ref_assainissement.stare.geom
				)
		)
)
SELECT identifianttraitement,
	typetraitement,
	recolement,
	id_com,
	texte,
	typeadministratifreseau,
	identifiantcoursdeau,
	identifiantbassinversantruisseau,
	identifiantbvgrand,
	identifiantsteu,
	nomsteu,
	identifiantcaptage,
	nomcaptage,
	geom
FROM ranked_results
WHERE rn = 1
ORDER BY identifianttraitement;
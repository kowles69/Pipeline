-- Parcelles
WITH parcelles_centroid AS (
	SELECT p.idparcelle,
		p.codenatureproprietaire,
		p.natureproprietaire,
		ST_Centroid(p.geom) as centroid,
		p.geom
	FROM pub_fed_cadastre.parcelleajour p
	WHERE p.codenatureproprietaire IN ('0', '5', '6', '7', '8', '10')
),
captages_prioritaires AS (
	SELECT DISTINCT ON (p.idparcelle) p.idparcelle,
		cp.identifiantcaptage,
		ca.nomcaptage
	FROM parcelles_centroid p
		JOIN ref_eaupotable.captageperim cp ON ST_Intersects(p.centroid, cp.geom)
		JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
	WHERE cp.niveau = 'E'
	ORDER BY p.idparcelle,
		CASE
			WHEN cp.identifiantcaptage = 'E565' THEN 2
			ELSE 1
		END -- Priorité aux autres captages
)
SELECT p.idparcelle,
	p.codenatureproprietaire,
	p.natureproprietaire,
	bv.identifiantbvgrand,
	bv.identifiantsteu,
	bv.nomsteu,
	com.id_com,
	com.texte,
	r.identifiantcoursdeau,
	r.identifiantbassinversantruisseau,
	cp.identifiantcaptage,
	cp.nomcaptage,
	p.geom
FROM parcelles_centroid p
	LEFT JOIN ref_assainissement.bvgrand bv ON p.centroid && bv.geom
	AND ST_Intersects(p.centroid, bv.geom)
	LEFT JOIN ref_cadastre.commune com ON p.centroid && com.geom
	AND ST_Intersects(p.centroid, com.geom)
	LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON p.centroid && r.geom
	AND ST_Intersects(p.centroid, r.geom)
	LEFT JOIN captages_prioritaires cp ON p.idparcelle = cp.idparcelle;
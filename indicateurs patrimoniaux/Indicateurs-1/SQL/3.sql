-- Canas
WITH canas_centroid AS (
    SELECT c.identifiantcanas,
        c.typereseau,
        c.precisionplanimetrique,
        ST_Centroid(c.geom) AS centroid
    FROM ref_assainissement.canas c
),
captages_prioritaires AS (
    SELECT DISTINCT ON (c.identifiantcanas) c.identifiantcanas,
        cp.identifiantcaptage,
        ca.nomcaptage
    FROM canas_centroid c
        JOIN ref_eaupotable.captageperim cp ON ST_Intersects(c.centroid, cp.geom)
        JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
    WHERE cp.niveau = 'E'
    ORDER BY c.identifiantcanas,
        CASE
            WHEN cp.identifiantcaptage = 'E565' THEN 2
            ELSE 1
        END -- Priorité aux autres captages
)
SELECT c.identifiantcanas,
    c.typereseau,
    c.precisionplanimetrique,
    bv.identifiantbvgrand,
    bv.identifiantsteu,
    bv.nomsteu,
    com.id_com,
    com.texte,
    r.identifiantcoursdeau,
    r.identifiantbassinversantruisseau,
    cp.identifiantcaptage,
    cp.nomcaptage
FROM canas_centroid c
    LEFT JOIN ref_assainissement.bvgrand bv ON ST_Intersects(c.centroid, bv.geom)
    LEFT JOIN ref_cadastre.commune com ON ST_Intersects(c.centroid, com.geom)
    LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON ST_Intersects(c.centroid, r.geom)
    LEFT JOIN captages_prioritaires cp ON c.identifiantcanas = cp.identifiantcanas;
-- Canaexp
WITH canaexp_centroid AS (
    SELECT c.idcanaexp,
        c.longueur,
        c.typreseau,
        c.typeffluen,
        c.noteindig,
        c.domanialit,
        c.hauteur,
        c.annereha,
        c.typeetude,
        ST_Centroid(c.geom) AS centroid
    FROM ref_assainissement.canaexp c
    WHERE c.domanialit = 'Métropole'
),
captages_prioritaires AS (
    SELECT DISTINCT ON (cc.idcanaexp) cc.idcanaexp,
        cp.identifiantcaptage,
        ca.nomcaptage
    FROM canaexp_centroid cc
        JOIN ref_eaupotable.captageperim cp ON ST_Intersects(cc.centroid, cp.geom)
        JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
    WHERE cp.niveau = 'E'
    ORDER BY cc.idcanaexp,
        CASE
            WHEN cp.identifiantcaptage = 'E565' THEN 2
            ELSE 1
        END -- Priorité aux autres captages
)
SELECT ce.idcanaexp,
    ce.longueur,
    ce.typreseau,
    ce.typeffluen,
    ce.noteindig,
    ce.domanialit,
    ce.hauteur,
    ce.annereha,
    ce.typeetude,
    bv.identifiantbvgrand,
    bv.identifiantsteu,
    bv.nomsteu,
    com.id_com,
    com.texte,
    r.identifiantcoursdeau,
    r.identifiantbassinversantruisseau,
    cp.identifiantcaptage,
    cp.nomcaptage
FROM canaexp_centroid ce
    LEFT JOIN ref_assainissement.bvgrand bv ON ST_Intersects(ce.centroid, bv.geom)
    LEFT JOIN ref_cadastre.commune com ON ST_Intersects(ce.centroid, com.geom)
    LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON ST_Intersects(ce.centroid, r.geom)
    LEFT JOIN captages_prioritaires cp ON ce.idcanaexp = cp.idcanaexp;
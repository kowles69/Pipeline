-- Canap
WITH canap_filtered AS (
    SELECT c.typeadministratifreseau,
        c.typeeffluent,
        c.identifiantcanap,
        c.longueur,
        c.domanialite,
        c.materiaupresume,
        c.materiau,
        c.hauteur,
        c.anneepose,
        c.anneeposeinferieur,
        c.anneeposesuperieur,
        c.precisionplanimetrique,
        c.geom,
        ST_Centroid(c.geom) AS centroid
    FROM ref_assainissement.canap c
    WHERE c.domanialite = 2
),
captages_prioritaires AS (
    SELECT DISTINCT ON (cf.identifiantcanap) cf.identifiantcanap,
        cp.identifiantcaptage,
        ca.nomcaptage
    FROM canap_filtered cf
        JOIN ref_eaupotable.captageperim cp ON ST_Intersects(cf.centroid, cp.geom)
        JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
    WHERE cp.niveau = 'E'
    ORDER BY cf.identifiantcanap,
        CASE
            WHEN cp.identifiantcaptage = 'E565' THEN 2
            ELSE 1
        END -- Priorité aux autres captages
)
SELECT c.typeadministratifreseau,
    c.typeeffluent,
    c.identifiantcanap,
    c.longueur,
    c.domanialite,
    c.materiaupresume,
    c.materiau,
    c.hauteur,
    c.anneepose,
    c.anneeposeinferieur,
    c.anneeposesuperieur,
    c.precisionplanimetrique,
    bv.identifiantbvgrand,
    bv.identifiantsteu,
    bv.nomsteu,
    com.id_com,
    com.texte,
    r.identifiantcoursdeau,
    r.identifiantbassinversantruisseau,
    cp.identifiantcaptage,
    cp.nomcaptage,
    c.geom
FROM canap_filtered c
    LEFT JOIN ref_assainissement.bvgrand bv ON ST_Intersects(c.centroid, bv.geom)
    LEFT JOIN ref_cadastre.commune com ON ST_Intersects(c.centroid, com.geom)
    LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON ST_Intersects(c.centroid, r.geom)
    LEFT JOIN captages_prioritaires cp ON c.identifiantcanap = cp.identifiantcanap;
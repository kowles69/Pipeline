-- Bassins
WITH bassin_centroid AS (
    SELECT b.identifiantbassin,
        b.nombassin,
        b.nature,
        b.typebassin,
        b.anneeconstruction,
        b.domanialite,
        b.exploitant,
        b.etat,
        b.volumeexploitation,
        ST_Centroid(b.geom) AS centroid
    FROM ref_assainissement.bassin b
    WHERE b.domanialite = 2
),
captages_prioritaires AS (
    SELECT DISTINCT ON (bc.identifiantbassin) bc.identifiantbassin,
        cp.identifiantcaptage,
        ca.nomcaptage
    FROM bassin_centroid bc
        JOIN ref_eaupotable.captageperim cp ON ST_Intersects(bc.centroid, cp.geom)
        JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
    WHERE cp.niveau = 'E'
    ORDER BY bc.identifiantbassin,
        CASE
            WHEN cp.identifiantcaptage = 'E565' THEN 2
            ELSE 1
        END -- Priorité aux autres captages
)
SELECT b.identifiantbassin,
    b.nombassin,
    b.nature,
    b.typebassin,
    b.anneeconstruction,
    b.domanialite,
    b.exploitant,
    b.etat,
    b.volumeexploitation,
    bv.identifiantbvgrand,
    bv.identifiantsteu,
    bv.nomsteu,
    com.id_com,
    com.texte,
    r.identifiantcoursdeau,
    r.identifiantbassinversantruisseau,
    cp.identifiantcaptage,
    cp.nomcaptage
FROM bassin_centroid b
    LEFT JOIN ref_assainissement.bvgrand bv ON ST_Intersects(b.centroid, bv.geom)
    LEFT JOIN ref_cadastre.commune com ON ST_Intersects(b.centroid, com.geom)
    LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON ST_Intersects(b.centroid, r.geom)
    LEFT JOIN captages_prioritaires cp ON b.identifiantbassin = cp.identifiantbassin;
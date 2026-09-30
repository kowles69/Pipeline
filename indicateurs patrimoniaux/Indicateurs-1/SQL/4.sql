-- Déversoir d'orage
WITH do_centroid AS (
    SELECT d.identifiantdevorage,
        d.datecreation,
        ST_Centroid(d.geom) AS centroid
    FROM ref_assainissement.devorage d
),
captages_prioritaires AS (
    SELECT DISTINCT ON (d.identifiantdevorage) d.identifiantdevorage,
        cp.identifiantcaptage,
        ca.nomcaptage
    FROM do_centroid d
        JOIN ref_eaupotable.captageperim cp ON ST_Intersects(d.centroid, cp.geom)
        JOIN ref_eaupotable.captage ca ON cp.identifiantcaptage = ca.identifiantcaptage
    WHERE cp.niveau = 'E'
    ORDER BY d.identifiantdevorage,
        CASE
            WHEN cp.identifiantcaptage = 'E565' THEN 2
            ELSE 1
        END -- Priorité aux autres captages
),
ranked_results AS (
    SELECT d.identifiantdevorage,
        (DATE_PART('year', d.datecreation) <= planrecol.anne_recol) AS recolement,
        bv.identifiantbvgrand,
        bv.identifiantsteu,
        bv.nomsteu,
        com.id_com,
        com.texte,
        r.identifiantcoursdeau,
        r.identifiantbassinversantruisseau,
        cp.identifiantcaptage,
        cp.nomcaptage,
        planrecol.identifiantplanrecol,
        ROW_NUMBER() OVER (
            PARTITION BY d.identifiantdevorage
            ORDER BY (DATE_PART('year', d.datecreation) <= planrecol.anne_recol) DESC
        ) AS rn
    FROM do_centroid d
        LEFT JOIN ref_assainissement.bvgrand bv ON ST_Intersects(d.centroid, bv.geom)
        LEFT JOIN ref_cadastre.commune com ON ST_Intersects(d.centroid, com.geom)
        LEFT JOIN ref_milieuxaquatiques.ruisseaubv r ON ST_Intersects(d.centroid, r.geom)
        LEFT JOIN captages_prioritaires cp ON d.identifiantdevorage = cp.identifiantdevorage
        LEFT JOIN (
            SELECT planrecol.identifiantplanrecol,
                planrecol.etatplanrecolement,
                EXTRACT(YEAR FROM planrecol.dateplanrecolement) as anne_recol,
                planrecol.geom
            FROM ref_assainissement.planrecol
            WHERE planrecol.etatplanrecolement = 'I'
        ) AS planrecol ON ST_Intersects(d.centroid, planrecol.geom)
)
SELECT
    identifiantdevorage,
    recolement,
    identifiantbvgrand,
    identifiantsteu,
    nomsteu,
    id_com,
    texte,
    identifiantcoursdeau,
    identifiantbassinversantruisseau,
    identifiantcaptage,
    nomcaptage
FROM
    ranked_results
WHERE
    rn = 1;

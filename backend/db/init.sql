CREATE TABLE IF NOT EXISTS teams (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  confederation VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fifa_rankings (
  id SERIAL PRIMARY KEY,
  team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  ranking_date DATE NOT NULL,
  rank INTEGER NOT NULL CHECK (rank > 0),
  points NUMERIC(8, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS matches (
  id SERIAL PRIMARY KEY,
  match_date DATE NOT NULL,
  tournament VARCHAR(100) NOT NULL,
  home_team_id INTEGER NOT NULL REFERENCES teams(id),
  away_team_id INTEGER NOT NULL REFERENCES teams(id),
  home_score INTEGER NOT NULL CHECK (home_score >= 0),
  away_score INTEGER NOT NULL CHECK (away_score >= 0),
  country VARCHAR(100) NOT NULL,
  neutral BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS predictions (
  id SERIAL PRIMARY KEY,
  home_team_id INTEGER NOT NULL REFERENCES teams(id),
  away_team_id INTEGER NOT NULL REFERENCES teams(id),
  match_date DATE NOT NULL,
  country VARCHAR(100) NOT NULL,
  neutral BOOLEAN NOT NULL DEFAULT TRUE,
  home_win_probability NUMERIC(5, 4) NOT NULL,
  draw_probability NUMERIC(5, 4) NOT NULL,
  away_win_probability NUMERIC(5, 4) NOT NULL,
  predicted_home_score INTEGER NOT NULL,
  predicted_away_score INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO teams (name, confederation) VALUES
  ('France', 'UEFA'),
  ('Japan', 'AFC'),
  ('Argentina', 'CONMEBOL'),
  ('Brazil', 'CONMEBOL'),
  ('England', 'UEFA'),
  ('Spain', 'UEFA'),
  ('Germany', 'UEFA'),
  ('Mexico', 'CONCACAF'),
  ('United States', 'CONCACAF'),
  ('Canada', 'CONCACAF'),
  ('Morocco', 'CAF'),
  ('Croatia', 'UEFA'),
  ('Belgium', 'UEFA'),
  ('Saudi Arabia', 'AFC'),
  ('Australia', 'AFC'),
  ('Uruguay', 'CONMEBOL'),
  ('Chile', 'CONMEBOL'),
  ('Colombia', 'CONMEBOL'),
  ('Venezuela', 'CONMEBOL')
ON CONFLICT (name) DO NOTHING;

INSERT INTO fifa_rankings (team_id, ranking_date, rank, points)
SELECT id, DATE '2026-01-01', rank, points
FROM (
  VALUES
    ('Argentina', 1, 1855.20),
    ('France', 2, 1845.44),
    ('Brazil', 5, 1784.09),
    ('England', 4, 1800.05),
    ('Spain', 8, 1732.64),
    ('Germany', 16, 1631.22),
    ('Japan', 18, 1614.33),
    ('Mexico', 14, 1652.70),
    ('United States', 12, 1665.27),
    ('Canada', 32, 1510.55),
    ('Morocco', 13, 1661.69),
    ('Croatia', 10, 1717.57),
    ('Belgium', 3, 1798.46),
    ('Saudi Arabia', 56, 1421.06),
    ('Australia', 25, 1539.22),
    ('Uruguay', 11, 1665.99),
    ('Chile', 42, 1489.82),
    ('Colombia', 9, 1727.21),
    ('Venezuela', 37, 1501.46)
) AS ranking_seed(team_name, rank, points)
JOIN teams ON teams.name = ranking_seed.team_name
WHERE NOT EXISTS (
  SELECT 1 FROM fifa_rankings
  WHERE fifa_rankings.team_id = teams.id
  AND fifa_rankings.ranking_date = DATE '2026-01-01'
);

INSERT INTO matches (
  match_date,
  tournament,
  home_team_id,
  away_team_id,
  home_score,
  away_score,
  country,
  neutral
)
SELECT match_date, tournament, home_team.id, away_team.id, home_score, away_score, country, neutral
FROM (
  VALUES
    (DATE '2018-07-10', 'World Cup', 'France', 'Belgium', 1, 0, 'Russia', TRUE),
    (DATE '2018-07-15', 'World Cup', 'France', 'Croatia', 4, 2, 'Russia', TRUE),
    (DATE '2022-11-22', 'World Cup', 'Argentina', 'Saudi Arabia', 1, 2, 'Qatar', TRUE),
    (DATE '2022-11-23', 'World Cup', 'France', 'Australia', 4, 1, 'Qatar', TRUE),
    (DATE '2022-12-01', 'World Cup', 'Japan', 'Spain', 2, 1, 'Qatar', TRUE),
    (DATE '2022-12-14', 'World Cup', 'France', 'Morocco', 2, 0, 'Qatar', TRUE),
    (DATE '2022-12-18', 'World Cup', 'Argentina', 'France', 3, 3, 'Qatar', TRUE),
    (DATE '2023-03-24', 'Friendly', 'Japan', 'Uruguay', 1, 1, 'Japan', FALSE),
    (DATE '2023-09-09', 'Friendly', 'Germany', 'Japan', 1, 4, 'Germany', FALSE),
    (DATE '2024-03-26', 'Friendly', 'France', 'Chile', 3, 2, 'France', FALSE),
    (DATE '2024-06-08', 'Friendly', 'United States', 'Colombia', 1, 5, 'United States', FALSE),
    (DATE '2024-07-01', 'Copa America', 'United States', 'Uruguay', 0, 1, 'United States', FALSE),
    (DATE '2024-07-05', 'Copa America', 'Canada', 'Venezuela', 1, 1, 'United States', TRUE),
    (DATE '2024-07-14', 'Euro', 'Spain', 'England', 2, 1, 'Germany', TRUE)
) AS match_seed(match_date, tournament, home_name, away_name, home_score, away_score, country, neutral)
JOIN teams AS home_team ON home_team.name = match_seed.home_name
JOIN teams AS away_team ON away_team.name = match_seed.away_name
WHERE NOT EXISTS (
  SELECT 1 FROM matches
  WHERE matches.match_date = match_seed.match_date
  AND matches.home_team_id = home_team.id
  AND matches.away_team_id = away_team.id
);

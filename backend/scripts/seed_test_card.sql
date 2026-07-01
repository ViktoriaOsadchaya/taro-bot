-- Временная тестовая карта для отладки UI до полного seed (78 карт).
-- Запуск: psql или DBeaver на БД taro_bot

INSERT INTO tarot_cards (code, name_ru, name_en, arcana, suit, number, image_path)
VALUES (
  'major_01_magician',
  'Тестовый Маг',
  'The Magician',
  'major',
  NULL,
  1,
  'https://via.placeholder.com/300x500?text=Magician'
)
ON CONFLICT (code) DO NOTHING;

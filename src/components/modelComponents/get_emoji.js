const emojiMap = {
  banana: "🍌",
  milk: "🥛",
  apple: "🍎",
  greenapple: "🍏",
  orange: "🍊",
  grapes: "🍇",
  strawberry: "🍓",
  watermelon: "🍉",
  pineapple: "🍍",
  lemon: "🍋",
  cherry: "🍒",
  peach: "🍑",
  pear: "🍐",
  mango: "🥭",
  avocado: "🥑",
  tomato: "🍅",
  carrot: "🥕",
  broccoli: "🥦",
  corn: "🌽",
  potato: "🥔",
  eggplant: "🍆",
  mushroom: "🍄",
  cucumber: "🥒",
  pepper: "🌶",
  leafygreen: "🥬",
  garlic: "🧄",
  onion: "🧅",
  beans: "🫘",
  peanuts: "🥜",
  chestnut: "🌰",
  bread: "🍞",
  croissant: "🥐",
  baguette: "🥖",
  pretzel: "🥨",
  bagel: "🥯",
  pancakes: "🥞",
  waffle: "🧇",
  cheese: "🧀",
  egg: "🥚",
  bacon: "🥓",
  meat: "🍖",
  poultry: "🍗",
  steak: "🥩",
  fish: "🐟",
  shrimp: "🍤",
  crab: "🦀",
  hotdog: "🌭",
  burger: "🍔",
  fries: "🍟",
  pizza: "🍕",
  taco: "🌮",
  burrito: "🌯",
  sandwich: "🥪",
  popcorn: "🍿",
  sushi: "🍣",
  ramen: "🍜",
  bento: "🍱",
  riceball: "🍙",
  ricecooked: "🍚",
  ricecracker: "🍘",
  curry: "🍛",
  oden: "🍢",
  dango: "🍡",
  dumpling: "🥟",
  mooncake: "🥮",
  fondue: "🫕",
  stuffedflatbread: "🥙",
  falafel: "🧆",
  tamale: "🌯",
  spaghetti: "🍝",
  stew: "🍲",
  canned: "🥫",
  icecream: "🍨",
  softice: "🍦",
  shavedice: "🍧",
  donut: "🍩",
  cookie: "🍪",
  cake: "🍰",
  cupcake: "🧁",
  pie: "🥧",
  chocolate: "🍫",
  candy: "🍬",
  lollipop: "🍭",
  honey: "🍯",
  rice: "🍚",
  ice: "🧊",
  water: "💧",
  beer: "🍺",
  wine: "🍷",
  champagne: "🥂",
  cocktail: "🍸",
  tropical: "🍹",
  tumbler: "🥃",
  foamglass: "🍻",
  sake: "🍶",
  tea: "🍵",
  coffee: "☕",
  teapot: "🫖",
  juicebox: "🧃",
  bubbletea: "🧋",
  soda: "🥤",
  cupwithstraw: "🥤",
  coconut: "🥥",
  kiwifruit: "🥝",
  blueberries: "🫐",
  melon: "🍈",
  olive: "🫒",
  roastedpotato: "🍠",
  bellpepper: "🫑",
  butter: "🧈",
  salt: "🧂",
  bowlwithspoon: "🥣",
  greensalad: "🥗",
  shallowpanoffood: "🥘",
  fortunecookie: "🥠",
  takeoutbox: "🥡",
  oyster: "🦪",
  fishcakewithswirl: "🍥",
  bottlewithpoppingcork: "🍾",
  babybottle: "🍼",
  mate: "🧉",
};

// Cache the keys for performance
const emojiKeys = Object.keys(emojiMap);

/**
 * Gets autocomplete suggestions based on a partial query.
 * @param {string} query - The partial text input by the user.
 * @returns {string[]} An array of matching suggestions.
 */
function getSuggestions(query) {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return [];
  }

  // Filter keys that start with the query and limit results for performance
  return emojiKeys
    .filter((key) => key.toLowerCase().startsWith(normalizedQuery))
    .slice(0, 7); // Show a maximum of 7 suggestions
}

/**
 * Finds the corresponding emoji for an exact term.
 * @param {string} term - The exact term to look up.
 * @returns {string} The corresponding emoji or an empty string if not found.
 */
function findEmoji(term) {
  const normalizedTerm = term.trim().toLowerCase();
  return emojiMap[normalizedTerm] || "";
}

export { getSuggestions, findEmoji };

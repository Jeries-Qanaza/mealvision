export default function getEmoji(text) {
  const emojiMap = {
    banana: '🍌', milk: '🥛', apple: '🍎', greenapple: '🍏', orange: '🍊',
    grapes: '🍇', strawberry: '🍓', watermelon: '🍉', pineapple: '🍍', lemon: '🍋',
    cherry: '🍒', peach: '🍑', pear: '🍐', mango: '🥭', avocado: '🥑', tomato: '🍅',
    carrot: '🥕', broccoli: '🥦', corn: '🌽', potato: '🥔', eggplant: '🍆',
    mushroom: '🍄', cucumber: '🥒', pepper: '🌶', leafygreen: '🥬', garlic: '🧄',
    onion: '🧅', beans: '🫘', peanuts: '🥜', chestnut: '🌰', bread: '🍞',
    croissant: '🥐', baguette: '🥖', pretzel: '🥨', bagel: '🥯', pancakes: '🥞',
    waffle: '🧇', cheese: '🧀', egg: '🥚', bacon: '🥓', meat: '🍖', poultry: '🍗',
    steak: '🥩', fish: '🐟', shrimp: '🍤', crab: '🦀', hotdog: '🌭', burger: '🍔',
    fries: '🍟', pizza: '🍕', taco: '🌮', burrito: '🌯', sandwich: '🥪', popcorn: '🍿',
    sushi: '🍣', ramen: '🍜', bento: '🍱', riceball: '🍙', ricecooked: '🍚',
    ricecracker: '🍘', curry: '🍛', oden: '🍢', dango: '🍡', dumpling: '🥟',
    mooncake: '🥮', fondue: '🫕', stuffedflatbread: '🥙', falafel: '🧆', tamale: '🌯',
    spaghetti: '🍝', stew: '🍲', canned: '🥫', icecream: '🍨', softice: '🍦',
    shavedice: '🍧', donut: '🍩', cookie: '🍪', cake: '🍰', cupcake: '🧁', pie: '🥧',
    chocolate: '🍫', candy: '🍬', lollipop: '🍭', honey: '🍯', rice: '🍚', ice: '🧊',
    water: '💧', beer: '🍺', wine: '🍷', champagne: '🥂', cocktail: '🍸',
    tropical: '🍹', tumbler: '🥃', foamglass: '🍻', sake: '🍶', teacup: '🍵',
    coffee: '☕', teapot: '🫖', juicebox: '🧃', bubbletea: '🧋', soda: '🥤',
    cupwithstraw: '🥤', coconut: '🥥', kiwifruit: '🥝', blueberries: '🫐', melon: '🍈',
    olive: '🫒', roastedpotato: '🍠', bellpepper: '🫑', butter: '🧈', salt: '🧂',
    bowlwithspoon: '🥣', greensalad: '🥗', shallowpanoffood: '🥘', fortunecookie: '🥠',
    takeoutbox: '🥡', oyster: '🦪', fishcakewithswirl: '🍥', bottlewithpoppingcork: '🍾', babybottle: '🍼', mate: '🧉'
  };
  return emojiMap[text] || "";
}

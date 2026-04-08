const Anthropic = require('@anthropic-ai/sdk');

exports.handler = async (event) => {
  const headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Content-Type': 'application/json'};
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
  if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: JSON.stringify({ detail: 'Method not allowed' }) };
  
  try {
    const { message } = JSON.parse(event.body);
    if (!message) return { statusCode: 400, headers, body: JSON.stringify({ detail: 'Empty message.' }) };
    
    const client = new Anthropic();
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 500,
      system: "Tu es MAX, l'assistant de CUE, une plateforme qui connecte les DJs avec les clubs et événements. Réponds en français, de manière concise et amicale. CUE propose: matching IA, contrats automatiques, paiements sécurisés via Stripe. Tarifs: Starter gratuit (7% commission), Pro DJ 29€/mois (3%), Business 149€/mois (0%).",
      messages: [{ role: "user", content: message }]
    });
    
    return { statusCode: 200, headers, body: JSON.stringify({ reply: response.content[0].text, sources: [], escalation: false }) };
  } catch (error) { 
    return { statusCode: 500, headers, body: JSON.stringify({ detail: error.message }) }; 
  }
};

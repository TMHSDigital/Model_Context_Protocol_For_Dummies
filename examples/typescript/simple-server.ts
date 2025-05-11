/**
 * Simple MCP Server Example
 * 
 * This demonstrates a basic MCP server that exposes both resources and tools.
 * It simulates a weather data service with:
 * - Resources: Current weather data for different cities
 * - Tools: Functions to convert temperatures and get forecasts
 */

import { Server, ServerOptions } from '@modelcontextprotocol/sdk';

// Initialize the server
const options: ServerOptions = {
  name: 'WeatherMCPServer',
  version: '1.0.0',
  features: {
    resources: true,
    tools: true,
    prompts: false
  }
};

const server = new Server(options);

// Simulated weather data
const weatherData = {
  'new-york': {
    city: 'New York',
    temperature: 72,
    condition: 'Partly Cloudy',
    humidity: 65,
    updatedAt: new Date().toISOString()
  },
  'london': {
    city: 'London',
    temperature: 16,
    condition: 'Rainy',
    humidity: 80,
    updatedAt: new Date().toISOString()
  },
  'tokyo': {
    city: 'Tokyo',
    temperature: 25,
    condition: 'Clear',
    humidity: 60,
    updatedAt: new Date().toISOString()
  }
};

// Register resource handlers
server.registerResourceHandler({
  // List available resources (cities)
  listResources: async () => {
    return {
      resources: Object.keys(weatherData).map(cityId => ({
        id: cityId,
        name: weatherData[cityId].city,
        description: `Current weather for ${weatherData[cityId].city}`
      }))
    };
  },
  
  // Read a specific resource (city weather data)
  readResource: async ({ resourceId }) => {
    if (resourceId in weatherData) {
      return {
        content: JSON.stringify(weatherData[resourceId], null, 2)
      };
    }
    
    throw new Error(`Weather data for ${resourceId} not found`);
  }
});

// Register tool handlers
server.registerToolHandler({
  // List available tools
  listTools: async () => {
    return {
      tools: [
        {
          name: 'convert_temperature',
          description: 'Convert temperature between Fahrenheit and Celsius',
          parameters: {
            type: 'object',
            properties: {
              temperature: {
                type: 'number',
                description: 'Temperature value to convert'
              },
              from_unit: {
                type: 'string',
                enum: ['celsius', 'fahrenheit'],
                description: 'Current temperature unit'
              },
              to_unit: {
                type: 'string',
                enum: ['celsius', 'fahrenheit'],
                description: 'Target temperature unit'
              }
            },
            required: ['temperature', 'from_unit', 'to_unit']
          }
        },
        {
          name: 'get_forecast',
          description: 'Get weather forecast for a city',
          parameters: {
            type: 'object',
            properties: {
              city: {
                type: 'string',
                description: 'City name'
              },
              days: {
                type: 'number',
                description: 'Number of days for forecast (1-7)'
              }
            },
            required: ['city']
          }
        }
      ]
    };
  },
  
  // Call a specific tool
  callTool: async ({ name, parameters }) => {
    if (name === 'convert_temperature') {
      const { temperature, from_unit, to_unit } = parameters as { 
        temperature: number; 
        from_unit: 'celsius' | 'fahrenheit'; 
        to_unit: 'celsius' | 'fahrenheit' 
      };
      
      if (from_unit === to_unit) {
        return { result: temperature };
      }
      
      let result: number;
      if (from_unit === 'celsius' && to_unit === 'fahrenheit') {
        result = (temperature * 9/5) + 32;
      } else {
        result = (temperature - 32) * 5/9;
      }
      
      return {
        result: {
          value: parseFloat(result.toFixed(1)),
          unit: to_unit
        }
      };
    }
    
    if (name === 'get_forecast') {
      const { city, days = 3 } = parameters as { city: string; days?: number };
      const normalizedCity = city.toLowerCase().replace(/\s+/g, '-');
      
      // Check if we have data for this city
      const cityData = Object.values(weatherData).find(
        data => data.city.toLowerCase() === city.toLowerCase()
      );
      
      if (!cityData) {
        throw new Error(`No weather data available for ${city}`);
      }
      
      // Generate a simulated forecast
      const forecast = [];
      const conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Stormy', 'Clear'];
      const baseTemp = cityData.temperature;
      
      for (let i = 1; i <= Math.min(days, 7); i++) {
        const variation = Math.floor(Math.random() * 10) - 5; // -5 to +5 degree variation
        forecast.push({
          day: i,
          date: new Date(Date.now() + i * 86400000).toISOString().split('T')[0],
          temperature: baseTemp + variation,
          condition: conditions[Math.floor(Math.random() * conditions.length)],
        });
      }
      
      return {
        result: {
          city: cityData.city,
          forecast
        }
      };
    }
    
    throw new Error(`Tool ${name} not found`);
  }
});

// Start the server
server.listen();

console.log('Weather MCP Server is running...'); 
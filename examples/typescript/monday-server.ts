/**
 * Monday.com MCP Server Example
 * 
 * This demonstrates an MCP server that integrates with Monday.com's GraphQL API.
 * It provides:
 * - Resources: Access to boards, items, and user information
 * - Tools: Functions to create and update items, assign users, etc.
 */

import { Server, ServerOptions } from '@modelcontextprotocol/sdk';
import fetch from 'node-fetch';

// Initialize the server
const options: ServerOptions = {
  name: 'MondayMCPServer',
  version: '1.0.0',
  features: {
    resources: true,
    tools: true,
    prompts: true
  }
};

const server = new Server(options);

// Configuration (in a real implementation, these would be securely stored/retrieved)
const MONDAY_API_URL = 'https://api.monday.com/v2';
const API_TOKEN = process.env.MONDAY_API_TOKEN || 'your-api-token';

// Helper function for GraphQL requests
async function queryMondayAPI(query: string, variables = {}) {
  const response = await fetch(MONDAY_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': API_TOKEN
    },
    body: JSON.stringify({ query, variables })
  });

  const data = await response.json();
  
  if (data.errors) {
    throw new Error(`Monday.com API Error: ${data.errors[0].message}`);
  }
  
  return data.data;
}

// Rate limiting implementation
const RATE_LIMITS = {
  dailyRemaining: 1000, // Depends on subscription tier
  resetTime: Date.now() + 86400000,
  activeRequests: 0
};

async function checkRateLimit() {
  if (RATE_LIMITS.dailyRemaining <= 0) {
    const resetTimeStr = new Date(RATE_LIMITS.resetTime).toISOString();
    throw new Error(`Rate limit exceeded. Resets at ${resetTimeStr}`);
  }
  
  if (RATE_LIMITS.activeRequests >= 10) {
    throw new Error('Too many concurrent requests. Please try again.');
  }
  
  RATE_LIMITS.dailyRemaining--;
  RATE_LIMITS.activeRequests++;
  
  return true;
}

function releaseRateLimit() {
  RATE_LIMITS.activeRequests--;
}

// Cache implementation for frequently accessed data
const CACHE = {
  boards: new Map(),
  boardStructure: new Map(),
  items: new Map(),
  users: new Map()
};

// Register resource handlers
server.registerResourceHandler({
  // List available resources
  listResources: async () => {
    try {
      await checkRateLimit();
      
      return {
        resources: [
          {
            id: 'list_boards',
            name: 'Boards',
            description: 'List all accessible boards'
          },
          {
            id: 'get_board_structure',
            name: 'Board Structure',
            description: 'Get the structure of a specific board'
          },
          {
            id: 'list_items_by_board',
            name: 'Items by Board',
            description: 'List all items in a specific board'
          },
          {
            id: 'list_items_by_status',
            name: 'Items by Status',
            description: 'List items filtered by status'
          },
          {
            id: 'list_overdue_items',
            name: 'Overdue Items',
            description: 'List items past their due dates'
          },
          {
            id: 'get_user_details',
            name: 'User Details',
            description: 'Get details about team members'
          },
          {
            id: 'get_user_workload',
            name: 'User Workload',
            description: 'View task distribution across team members'
          }
        ]
      };
    } finally {
      releaseRateLimit();
    }
  },
  
  // Read a specific resource
  readResource: async ({ resourceId, parameters }) => {
    try {
      await checkRateLimit();
      
      switch (resourceId) {
        case 'list_boards':
          return await listBoards();
        
        case 'get_board_structure':
          if (!parameters?.board_id) {
            throw new Error('board_id parameter is required');
          }
          return await getBoardStructure(parameters.board_id);
        
        case 'list_items_by_board':
          if (!parameters?.board_id) {
            throw new Error('board_id parameter is required');
          }
          return await listItemsByBoard(parameters.board_id);
        
        case 'list_items_by_status':
          if (!parameters?.board_id || !parameters?.status) {
            throw new Error('board_id and status parameters are required');
          }
          return await listItemsByStatus(parameters.board_id, parameters.status);
        
        case 'list_overdue_items':
          return await listOverdueItems();
        
        case 'get_user_details':
          if (!parameters?.user_id) {
            throw new Error('user_id parameter is required');
          }
          return await getUserDetails(parameters.user_id);
        
        case 'get_user_workload':
          if (!parameters?.user_id) {
            throw new Error('user_id parameter is required');
          }
          return await getUserWorkload(parameters.user_id);
        
        default:
          throw new Error(`Resource ${resourceId} not found`);
      }
    } finally {
      releaseRateLimit();
    }
  }
});

// Resource implementation functions
async function listBoards() {
  // Check cache first
  if (CACHE.boards.has('all') && CACHE.boards.get('all').timestamp > Date.now() - 300000) {
    return { content: JSON.stringify(CACHE.boards.get('all').data) };
  }
  
  const query = `
    query {
      boards {
        id
        name
        description
        state
        board_kind
        updated_at
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  
  // Store in cache for 5 minutes
  CACHE.boards.set('all', {
    timestamp: Date.now(),
    data: result.boards
  });
  
  return { content: JSON.stringify(result.boards) };
}

async function getBoardStructure(boardId: string) {
  // Check cache first
  const cacheKey = `structure-${boardId}`;
  if (CACHE.boardStructure.has(cacheKey) && CACHE.boardStructure.get(cacheKey).timestamp > Date.now() - 300000) {
    return { content: JSON.stringify(CACHE.boardStructure.get(cacheKey).data) };
  }
  
  const query = `
    query {
      boards(ids: ${boardId}) {
        columns {
          id
          title
          type
          settings_str
        }
        groups {
          id
          title
          color
          position
        }
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  const boardStructure = result.boards[0];
  
  // Store in cache for 5 minutes
  CACHE.boardStructure.set(cacheKey, {
    timestamp: Date.now(),
    data: boardStructure
  });
  
  return { content: JSON.stringify(boardStructure) };
}

async function listItemsByBoard(boardId: string) {
  const query = `
    query {
      boards(ids: ${boardId}) {
        name
        items {
          id
          name
          state
          column_values {
            id
            title
            text
            value
          }
          created_at
          updated_at
        }
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  return { content: JSON.stringify(result.boards[0]) };
}

async function listItemsByStatus(boardId: string, status: string) {
  // First, get the status column id
  const boardStructure = await getBoardStructure(boardId);
  const parsedStructure = JSON.parse(boardStructure.content);
  
  const statusColumn = parsedStructure.columns.find(col => col.type === 'status');
  if (!statusColumn) {
    throw new Error('Status column not found on this board');
  }
  
  const query = `
    query {
      boards(ids: ${boardId}) {
        items {
          id
          name
          column_values(ids: ["${statusColumn.id}"]) {
            text
          }
          created_at
          updated_at
        }
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  
  // Filter items by status
  const filteredItems = result.boards[0].items.filter(item => {
    return item.column_values[0].text.toLowerCase() === status.toLowerCase();
  });
  
  return { content: JSON.stringify(filteredItems) };
}

async function listOverdueItems() {
  const query = `
    query {
      items_by_column_values(
        board_id: ALL_BOARDS
        column_id: "date"
        column_value: "overdue"
      ) {
        id
        name
        board {
          id
          name
        }
        column_values {
          title
          text
        }
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  return { content: JSON.stringify(result.items_by_column_values) };
}

async function getUserDetails(userId: string) {
  // Check cache first
  if (CACHE.users.has(userId) && CACHE.users.get(userId).timestamp > Date.now() - 300000) {
    return { content: JSON.stringify(CACHE.users.get(userId).data) };
  }
  
  const query = `
    query {
      users(ids: ${userId}) {
        id
        name
        email
        title
        photo_thumb
        created_at
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  
  // Store in cache for 5 minutes
  CACHE.users.set(userId, {
    timestamp: Date.now(),
    data: result.users[0]
  });
  
  return { content: JSON.stringify(result.users[0]) };
}

async function getUserWorkload(userId: string) {
  const query = `
    query {
      items_by_person_id(
        person_id: ${userId}
      ) {
        id
        name
        board {
          id
          name
        }
        column_values {
          id
          title
          text
        }
      }
    }
  `;
  
  const result = await queryMondayAPI(query);
  return { content: JSON.stringify(result.items_by_person_id) };
}

// Register tool handlers
server.registerToolHandler({
  // List available tools
  listTools: async () => {
    return {
      tools: [
        {
          name: 'create_item',
          description: 'Create a new item on a board',
          parameters: {
            type: 'object',
            properties: {
              board_id: {
                type: 'number',
                description: 'The ID of the board'
              },
              group_id: {
                type: 'string',
                description: 'The ID of the group to add the item to'
              },
              item_name: {
                type: 'string',
                description: 'The name of the item to create'
              },
              column_values: {
                type: 'object',
                description: 'Column values for the new item'
              }
            },
            required: ['board_id', 'item_name']
          }
        },
        {
          name: 'update_item_status',
          description: 'Update the status of an item',
          parameters: {
            type: 'object',
            properties: {
              item_id: {
                type: 'number',
                description: 'The ID of the item'
              },
              status_column_id: {
                type: 'string',
                description: 'The ID of the status column'
              },
              new_status: {
                type: 'string',
                description: 'The new status value'
              }
            },
            required: ['item_id', 'status_column_id', 'new_status']
          }
        },
        {
          name: 'assign_user_to_item',
          description: 'Assign a user to an item',
          parameters: {
            type: 'object',
            properties: {
              item_id: {
                type: 'number',
                description: 'The ID of the item'
              },
              user_id: {
                type: 'number',
                description: 'The ID of the user to assign'
              },
              person_column_id: {
                type: 'string',
                description: 'The ID of the person column'
              }
            },
            required: ['item_id', 'user_id', 'person_column_id']
          }
        },
        {
          name: 'add_update_to_item',
          description: 'Add an update/comment to an item',
          parameters: {
            type: 'object',
            properties: {
              item_id: {
                type: 'number',
                description: 'The ID of the item'
              },
              update_text: {
                type: 'string',
                description: 'The text of the update'
              }
            },
            required: ['item_id', 'update_text']
          }
        }
      ]
    };
  },
  
  // Call a specific tool
  callTool: async ({ name, parameters }) => {
    try {
      await checkRateLimit();
      
      switch (name) {
        case 'create_item':
          return await createItem(parameters);
        
        case 'update_item_status':
          return await updateItemStatus(parameters);
        
        case 'assign_user_to_item':
          return await assignUserToItem(parameters);
        
        case 'add_update_to_item':
          return await addUpdateToItem(parameters);
        
        default:
          throw new Error(`Tool ${name} not found`);
      }
    } finally {
      releaseRateLimit();
    }
  }
});

// Tool implementation functions
async function createItem(parameters) {
  const { board_id, group_id, item_name, column_values } = parameters;
  
  const columnValuesJson = JSON.stringify(column_values || {});
  
  const mutation = `
    mutation {
      create_item(
        board_id: ${board_id},
        ${group_id ? `group_id: "${group_id}",` : ''}
        item_name: "${item_name}",
        column_values: '${columnValuesJson}'
      ) {
        id
        name
      }
    }
  `;
  
  const result = await queryMondayAPI(mutation);
  
  return {
    result: {
      id: result.create_item.id,
      name: result.create_item.name,
      message: "Item created successfully"
    }
  };
}

async function updateItemStatus(parameters) {
  const { item_id, status_column_id, new_status } = parameters;
  
  const columnValue = JSON.stringify({
    label: new_status
  });
  
  const mutation = `
    mutation {
      change_column_value(
        item_id: ${item_id},
        column_id: "${status_column_id}",
        value: '${columnValue}'
      ) {
        id
        name
      }
    }
  `;
  
  const result = await queryMondayAPI(mutation);
  
  return {
    result: {
      id: result.change_column_value.id,
      message: "Status updated successfully"
    }
  };
}

async function assignUserToItem(parameters) {
  const { item_id, user_id, person_column_id } = parameters;
  
  const columnValue = JSON.stringify({
    personsAndTeams: [
      {
        id: user_id,
        kind: "person"
      }
    ]
  });
  
  const mutation = `
    mutation {
      change_column_value(
        item_id: ${item_id},
        column_id: "${person_column_id}",
        value: '${columnValue}'
      ) {
        id
        name
      }
    }
  `;
  
  const result = await queryMondayAPI(mutation);
  
  return {
    result: {
      id: result.change_column_value.id,
      message: "User assigned successfully"
    }
  };
}

async function addUpdateToItem(parameters) {
  const { item_id, update_text } = parameters;
  
  const mutation = `
    mutation {
      create_update(
        item_id: ${item_id},
        body: "${update_text}"
      ) {
        id
        text
      }
    }
  `;
  
  const result = await queryMondayAPI(mutation);
  
  return {
    result: {
      id: result.create_update.id,
      message: "Update added successfully"
    }
  };
}

// Register prompt handlers for common workflows
server.registerPromptHandler({
  listPrompts: async () => {
    return {
      prompts: [
        {
          id: 'project_initiation',
          name: 'Project Initiation',
          description: 'Start a new project with initial tasks and team assignments'
        },
        {
          id: 'sprint_planning',
          name: 'Sprint Planning',
          description: 'Move items from backlog to current sprint with estimates and priorities'
        },
        {
          id: 'risk_management',
          name: 'Risk Management',
          description: 'Identify and escalate tasks at risk'
        }
      ]
    };
  },
  
  readPrompt: async ({ promptId }) => {
    switch (promptId) {
      case 'project_initiation':
        return {
          content: JSON.stringify({
            name: 'Project Initiation',
            description: 'Start a new project with initial tasks and team assignments',
            steps: [
              {
                id: 'create_board',
                type: 'input',
                label: 'Create a new project board',
                fields: [
                  {
                    id: 'board_name',
                    label: 'Project Name',
                    type: 'text',
                    required: true
                  },
                  {
                    id: 'template_id',
                    label: 'Template',
                    type: 'select',
                    options: [
                      { label: 'Basic Project', value: '1' },
                      { label: 'Scrum', value: '2' },
                      { label: 'Kanban', value: '3' }
                    ],
                    required: true
                  }
                ]
              },
              {
                id: 'assign_team',
                type: 'input',
                label: 'Assign Team Members',
                fields: [
                  {
                    id: 'team_members',
                    label: 'Team Members',
                    type: 'multiselect',
                    dynamicOptions: 'users',
                    required: true
                  }
                ]
              },
              {
                id: 'setup_tasks',
                type: 'input',
                label: 'Set Up Initial Tasks',
                fields: [
                  {
                    id: 'tasks',
                    label: 'Tasks',
                    type: 'textarea',
                    placeholder: 'Enter tasks (one per line)',
                    required: true
                  }
                ]
              }
            ]
          })
        };
      
      case 'sprint_planning':
        return {
          content: JSON.stringify({
            name: 'Sprint Planning',
            description: 'Move items from backlog to current sprint with estimates and priorities',
            steps: [
              {
                id: 'select_board',
                type: 'input',
                label: 'Select Project Board',
                fields: [
                  {
                    id: 'board_id',
                    label: 'Board',
                    type: 'select',
                    dynamicOptions: 'boards',
                    required: true
                  }
                ]
              },
              {
                id: 'select_backlog_items',
                type: 'input',
                label: 'Select Backlog Items for Sprint',
                fields: [
                  {
                    id: 'backlog_items',
                    label: 'Backlog Items',
                    type: 'multiselect',
                    dynamicOptions: 'items_by_status',
                    required: true
                  }
                ]
              },
              {
                id: 'set_estimates',
                type: 'input',
                label: 'Set Estimates and Priorities',
                fields: [
                  {
                    id: 'due_date',
                    label: 'Sprint End Date',
                    type: 'date',
                    required: true
                  }
                ]
              }
            ]
          })
        };
      
      case 'risk_management':
        return {
          content: JSON.stringify({
            name: 'Risk Management',
            description: 'Identify and escalate tasks at risk',
            steps: [
              {
                id: 'select_project',
                type: 'input',
                label: 'Select Project',
                fields: [
                  {
                    id: 'board_id',
                    label: 'Board',
                    type: 'select',
                    dynamicOptions: 'boards',
                    required: true
                  }
                ]
              },
              {
                id: 'identify_risks',
                type: 'display',
                label: 'Identifying Tasks at Risk...',
                computedContent: 'delayed_tasks'
              },
              {
                id: 'escalate_risks',
                type: 'input',
                label: 'Escalate Selected Risks',
                fields: [
                  {
                    id: 'risk_items',
                    label: 'Items at Risk',
                    type: 'multiselect',
                    dynamicOptions: 'delayed_tasks',
                    required: true
                  },
                  {
                    id: 'notify_users',
                    label: 'Notify',
                    type: 'multiselect',
                    dynamicOptions: 'users',
                    required: true
                  },
                  {
                    id: 'escalation_message',
                    label: 'Message',
                    type: 'textarea',
                    required: true
                  }
                ]
              }
            ]
          })
        };
      
      default:
        throw new Error(`Prompt ${promptId} not found`);
    }
  }
});

// Start the server
server.listen();

console.log('Monday.com MCP Server is running...'); 
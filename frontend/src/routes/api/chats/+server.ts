import { json } from '@sveltejs/kit';
import type { RequestHandler } from '@sveltejs/kit';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export const GET: RequestHandler = async () => {
  const chats = await prisma.chat.findMany({
    include: { messages: true },
    orderBy: { updatedAt: 'desc' }
  });
  return json(chats);
};

export const POST: RequestHandler = async ({ request }) => {
  const { title, messages } = await request.json();
  console.log('📥 Creating new chat in database:', {
    title,
    messageCount: messages.length
  });

  try {
    const chat = await prisma.chat.create({
      data: {
        title,
        messages: {
          create: messages.map(({ role, content }) => ({
            role,
            content
          }))
        }
      },
      include: { messages: true }
    });
    console.log('✅ Chat created successfully:', {
      chatId: chat.id,
      messageCount: chat.messages.length
    });
    return json(chat);
  } catch (error) {
    console.error('❌ Failed to create chat:', error);
    throw error;
  }
};

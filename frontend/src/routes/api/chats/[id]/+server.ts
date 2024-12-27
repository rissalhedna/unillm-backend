import { json } from '@sveltejs/kit';
import type { RequestHandler } from '@sveltejs/kit';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export const GET: RequestHandler = async ({ params }) => {
  const chat = await prisma.chat.findUnique({
    where: { id: params.id },
    include: { messages: true }
  });
  return json(chat);
};

export const PATCH: RequestHandler = async ({ params, request }) => {
  const { title } = await request.json();
  const chat = await prisma.chat.update({
    where: { id: params.id },
    data: { title }
  });
  return json(chat);
};

export const DELETE: RequestHandler = async ({ params }) => {
  await prisma.chat.delete({
    where: { id: params.id }
  });
  return new Response(null, { status: 204 });
};

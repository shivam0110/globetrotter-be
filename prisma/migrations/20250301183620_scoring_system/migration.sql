/*
  Warnings:

  - You are about to drop the `game_sessions` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "game_sessions" DROP CONSTRAINT "game_sessions_user_id_fkey";

-- AlterTable
ALTER TABLE "users" ADD COLUMN     "best_try" INTEGER NOT NULL DEFAULT 0;

-- DropTable
DROP TABLE "game_sessions";

/*
  Warnings:

  - You are about to drop the column `correct_answers` on the `users` table. All the data in the column will be lost.
  - You are about to drop the column `incorrect_answers` on the `users` table. All the data in the column will be lost.
  - You are about to drop the column `score` on the `users` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "users" DROP COLUMN "correct_answers",
DROP COLUMN "incorrect_answers",
DROP COLUMN "score";

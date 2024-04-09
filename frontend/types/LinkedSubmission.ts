import Submission from '@/types/Submission.ts'

export default interface LinkedSubmission {
  id: number,
  submission: Submission,
  submission_id?: number,
  display_position: number,
}

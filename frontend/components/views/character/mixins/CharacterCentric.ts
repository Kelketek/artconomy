import {Component, mixins, Prop} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {CharacterController} from '@/store/characters/controller.ts'
import {flatten} from '@/lib/lib.ts'

@Component
export default class CharacterCentric extends mixins(Subjective) {
  public character: CharacterController = null as unknown as CharacterController
  @Prop({required: true})
  public characterName!: string

  public created() {
    this.character = this.$getCharacter(`character__${flatten(this.username)}__${flatten(this.characterName)}`, {
      characterName: this.characterName,
      username: this.username,
    })
  }
}

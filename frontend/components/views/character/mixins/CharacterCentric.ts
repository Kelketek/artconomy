import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Subjective from '@/mixins/subjective'
import {CharacterController} from '@/store/characters/controller'
import {flatten} from '@/lib/lib'

@Component
export default class CharacterCentric extends mixins(Subjective) {
  public character: CharacterController = null as unknown as CharacterController
  @Prop({required: true})
  public characterName!: string

  // Should be defined elsewhere, usually by subjective mixin.
  public username!: string

  public created() {
    this.character = this.$getCharacter(`character__${flatten(this.username)}__${flatten(this.characterName)}`, {
      characterName: this.characterName, username: this.username,
    })
  }
}

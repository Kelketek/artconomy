<template>
  <v-container fluid class="pa-0">
    <v-row class="d-flex">
      <v-col class="text-right">
        <v-btn color="green" @click="showNew = true" v-if="controls" variant="flat">
          <v-icon left icon="mdi-plus"/>
          New Character
        </v-btn>
      </v-col>
    </v-row>
    <ac-paginated :list="characters">
      <v-col class="pa-1" lg="2" md="3" cols="6" v-for="character in characters.list" :key="character.x!.id">
        <ac-character-preview :character="character.x" :key="character.x!.id"></ac-character-preview>
      </v-col>
    </ac-paginated>
    <ac-form-dialog
        v-if="controls"
        v-model="showNew"
        v-bind="form.bind"
        title="New Character"
        @submit="form.submitThen(visitCharacter)"
    >
      <v-row no-gutters>
        <v-col cols="12">
          <ac-bound-field :field="form.fields.name" hint="Enter the name of your character." label="Character Name">

          </ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="form.fields.private"
                          field-type="ac-checkbox"
                          :persistent-hint="true"
                          label="Private"
                          hint="If checked, this character will not appear in search listings and will only be visible to users you explicitly share them with."
          >
          </ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="form.fields.nsfw"
                          field-type="ac-checkbox"
                          :persistent-hint="true"
                          label="NSFW"
                          hint="If checked, this character will be hidden for users in SFW mode, or if they're
                          blocking a tag this character has in their NSFW blocked tags list. We recommend checking this
                          if you primarily draw/commission art of this character not appropriate for most workplace
                          settings."
          >
          </ac-bound-field>
        </v-col>
      </v-row>
    </ac-form-dialog>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {ListController} from '@/store/lists/controller.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {flatten} from '@/lib/lib.ts'

@Component({
  components: {
    AcBoundField,
    AcFormDialog,
    AcPaginated,
    AcCharacterPreview,
  },
})
class Characters extends mixins(Subjective) {
  public characters: ListController<Character> = null as unknown as ListController<Character>
  public form: FormController = null as unknown as FormController
  public showNew = false

  public get url() {
    return `/api/profiles/account/${this.username}/characters/`
  }

  public visitCharacter(character: Character) {
    this.$router.push({
      name: 'Character',
      params: {
        username: this.username,
        characterName: character.name,
      },
      query: {editing: 'true'},
    })
  }

  public created() {
    this.characters = this.$getList(`${flatten(this.username)}-characters`, {
      endpoint: this.url,
      keyProp: 'name',
    })
    this.form = this.$getForm(`${flatten(this.username)}-newCharacter`, {
      endpoint: this.url,
      fields: {
        name: {value: ''},
        private: {value: false},
        nsfw: {value: false},
      },
    })
    this.characters.firstRun().then()
  }
}

export default toNative(Characters)
</script>

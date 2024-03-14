<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-tooltip top v-if="editable" aria-label="Tooltip for edit character button">
        <template v-slot:activator="{props}">
          <v-btn v-bind="props" @click="toggle=true" color="accent" icon size="small" class="mr-1">
            <v-icon :icon="mdiAccount" size="x-large"/>
          </v-btn>
        </template>
        Edit Characters
      </v-tooltip>
      <v-tooltip top v-else aria-label="Tooltip for character listing">
        <template v-slot:activator="{props}">
          <v-icon v-bind="props" :icon="mdiAccountGroup"/>
        </template>
        Characters
      </v-tooltip>
      <v-col align-self="center" v-if="controller.empty">
        No characters tagged.
      </v-col>
      <ac-mini-character :character="item.x!.character" v-for="item in controller.list" :key="item.x!.id" :alt="item.x!.character.name" class="mr-1"/>
      <ac-expanded-property v-model="toggle" v-if="editable" aria-label="Character editing dialog">
        <template v-slot:title>Characters</template>
        <ac-related-manager
            :field-controller="tagCharacter.fields.character_id" :list-controller="controller"
            item-key="character"
        >
          <template v-slot:preview="{item}">
              <ac-mini-character :character="item.x.character" :removable="true"
                                 :alt="item.x.character.name"
                                 @remove="item.delete().catch(tagCharacter.setErrors)" class="mr-1"/>
          </template>
          <template v-slot:default="{filter}">
            <v-row class="mt-1">
              <v-col cols="12">
                <ac-bound-field
                    label="Tag Character"
                    hint="Enter the name of a character to tag them."
                    :field="tagCharacter.fields.character_id" field-type="ac-character-select" :multiple="false"
                    :filter="filter" :tagging="true"/>
              </v-col>
            </v-row>
          </template>
        </ac-related-manager>
      </ac-expanded-property>
    </v-row>
  </ac-load-section>
</template>

<script lang="ts">
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import AcRelatedManager from '../../wrappers/AcRelatedManager.vue'
import AcAvatar from '../../AcAvatar.vue'
import {ListController} from '@/store/lists/controller.ts'
import {Component, Prop, toNative} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {ArtVue} from '@/lib/lib.ts'
import LinkedCharacter from '@/types/LinkedCharacter.ts'
import {mdiAccountGroup, mdiAccount} from '@mdi/js'

@Component({
  components: {
    AcMiniCharacter,
    AcBoundField,
    AcExpandedProperty,
    AcAvatar,
    AcRelatedManager,
    AcLoadSection,
  },
})
class AcCharacterDisplay extends ArtVue {
  @Prop({required: true})
  public controller!: ListController<LinkedCharacter>

  public tagCharacter: FormController = null as unknown as FormController
  public toggle = false
  @Prop({required: true})
  public editable!: boolean
  public mdiAccount = mdiAccount
  public mdiAccountGroup = mdiAccountGroup

  public created() {
    this.tagCharacter = this.$getForm(
        this.controller.name + '__tagCharacter', {
          fields: {character_id: {value: null}},
          endpoint: this.controller.endpoint,
        })
  }
}

export default toNative(AcCharacterDisplay)
</script>

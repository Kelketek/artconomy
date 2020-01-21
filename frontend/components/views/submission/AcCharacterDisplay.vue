<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-col class="shrink">
        <v-tooltip top v-if="editable">
          <template v-slot:activator="{on}">
            <v-btn v-on="on" @click="toggle=true" color="accent" small fab><v-icon>people</v-icon></v-btn>
          </template>
          Edit Characters
        </v-tooltip>
        <v-tooltip top v-else>
          <template v-slot:activator="{on}">
            <v-icon>people</v-icon>
          </template>
          Characters
        </v-tooltip>
      </v-col>
      <v-col align-self="center" v-if="controller.empty">
          No characters tagged.
      </v-col>
      <v-col class="shrink" v-for="item in controller.list" :key="item.x.id">
        <ac-mini-character :character="item.x.character" />
      </v-col>
      <ac-expanded-property v-model="toggle" v-if="editable">
        <span slot="title">Characters</span>
        <ac-related-manager
            :field-controller="tagCharacter.fields.character_id" :list-controller="controller"
            item-key="character"
        >
          <template v-slot:preview="{item}">
            <v-col cols="4" sm="3" md="2" lg="1">
              <ac-mini-character :character="item.x.character" :removable="true" @remove="item.delete().catch(tagCharacter.setErrors)"/>
            </v-col>
          </template>
          <template v-slot:default="{filter}">
            <ac-bound-field
                label="Tag Character"
                hint="Enter the name of a character to tag them."
                :field="tagCharacter.fields.character_id" field-type="ac-character-select" :multiple="false" :filter="filter" :tagging="true" />
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
import {ListController} from '@/store/lists/controller'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {Prop} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import Vue from 'vue'
import Component from 'vue-class-component'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'

  @Component({components: {
    AcMiniCharacter,
    AcBoundField,
    AcExpandedProperty,
    AcAvatar,
    AcRelatedManager,
    AcLoadSection}})
export default class AcCharacterDisplay extends Vue {
    @Prop({required: true})
    public controller!: ListController<TerseUser>
    public tagCharacter: FormController = null as unknown as FormController
    public toggle = false
    @Prop({required: true})
    public editable!: boolean

    public created() {
      this.tagCharacter = this.$getForm(
        this.controller.name + '__tagCharacter', {
          fields: {character_id: {value: null}}, endpoint: this.controller.endpoint,
        })
    }
}
</script>

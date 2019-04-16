<template>
  <ac-load-section :controller="controller">
    <v-layout row wrap>
      <v-tooltip top v-if="editable">
        <template v-slot:activator="{on}">
          <v-btn v-on="on" @click="toggle=true" color="secondary" icon><v-icon>palette</v-icon></v-btn>
        </template>
        Edit Artists
      </v-tooltip>
      <v-tooltip top v-else>
        <template v-slot:activator="{on}">
          <v-icon>palette</v-icon>
        </template>
        Artists
      </v-tooltip>
      <v-flex v-if="controller.empty" d-flex>
        <v-layout row wrap justify-content align-center>
          <v-flex>No artists tagged.<span v-if="editable"></span></v-flex>
        </v-layout>
      </v-flex>
      <ac-avatar v-for="artist in controller.list" :user="artist.x.user" :key="artist.x.id" class="px-1"></ac-avatar>
      <ac-expanded-property v-model="toggle" v-if="editable">
        <span slot="title">Artists</span>
        <ac-related-manager
            :field-controller="tagArtist.fields.user_id" :list-controller="controller"
            item-key="user"
        >
          <template v-slot:preview="{item}">
            <v-flex xs4 sm3 md2 lg1>
              <ac-avatar :user="item.x.user" :removable="true" @remove="item.delete().catch(tagArtist.setErrors)"/>
            </v-flex>
          </template>
          <template v-slot:default="{filter}">
            <ac-bound-field
                label="Tag Artist"
                hint="Enter the username of another Artconomy user to tag them as an artist."
                :field="tagArtist.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter" :tagging="true" />
          </template>
        </ac-related-manager>
      </ac-expanded-property>
    </v-layout>
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

  @Component({components: {AcBoundField, AcExpandedProperty, AcAvatar, AcRelatedManager, AcLoadSection}})
export default class AcArtistDisplay extends Vue {
    @Prop({required: true})
    public controller!: ListController<TerseUser>
    public tagArtist: FormController = null as unknown as FormController
    @Prop({required: true})
    public submissionId!: number
    public toggle = false
    @Prop({required: true})
    public editable!: boolean

    public created() {
      this.tagArtist = this.$getForm(
        this.controller.name + '__tagArtist', {
          fields: {user_id: {value: null}}, endpoint: this.controller.endpoint,
        })
    }
}
</script>

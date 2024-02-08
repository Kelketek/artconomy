<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-tooltip top v-if="editable">
        <template v-slot:activator="{props}">
          <v-btn v-bind="props" @click="toggle=true" color="secondary" icon size="small" class="mr-1">
            <v-icon icon="mdi-palette" size="x-large" />
          </v-btn>
        </template>
        Edit Artists
      </v-tooltip>
      <v-tooltip top v-else>
        <template v-slot:activator="{props}">
          <v-icon v-bind="props" icon="mdi-palette"/>
        </template>
        Artists
      </v-tooltip>
      <v-col v-if="controller.empty" align-self="center">
        No artists tagged.
      </v-col>
      <ac-avatar :user="artist.x!.user" v-for="artist in controller.list" :key="artist.x!.id" class="mr-1"/>
      <ac-expanded-property v-model="toggle" v-if="editable">
        <template v-slot:title>Artists</template>
        <ac-related-manager
            :field-controller="tagArtist.fields.user_id" :list-controller="controller"
            item-key="user"
        >
          <template v-slot:preview="{item}">
            <ac-avatar :user="item.x.user" :removable="true" @remove="item.delete().catch(tagArtist.setErrors)" class="mr-1"/>
          </template>
          <template v-slot:default="{filter}">
            <v-row class="mt-1">
              <v-col cols="12">
                <ac-bound-field
                    label="Tag Artist"
                    hint="Enter the username of another Artconomy user to tag them as an artist."
                    :field="tagArtist.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"
                    :tagging="true"/>
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
import ArtistTag from '@/types/ArtistTag.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component({
  components: {
    AcBoundField,
    AcExpandedProperty,
    AcAvatar,
    AcRelatedManager,
    AcLoadSection,
  },
})
class AcArtistDisplay extends ArtVue {
  @Prop({required: true})
  public controller!: ListController<ArtistTag>

  public tagArtist: FormController = null as unknown as FormController
  @Prop({required: true})
  public submissionId!: number

  public toggle = false
  @Prop({required: true})
  public editable!: boolean

  public created() {
    this.tagArtist = this.$getForm(
        this.controller.name + '__tagArtist', {
          fields: {user_id: {value: null}},
          endpoint: this.controller.endpoint,
        })
  }
}

export default toNative(AcArtistDisplay)
</script>

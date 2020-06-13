<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-container fluid class="pa-0">
    <v-row dense>
      <v-col class="shrink">
        <v-tooltip top v-if="controls">
          <template v-slot:activator="{on}">
            <v-btn color="primary" fab small v-on="on" @click="editTags" class="edit-button"><v-icon>fa-tags</v-icon></v-btn>
          </template>
          Edit Tags
        </v-tooltip>
        <v-tooltip top v-else>
          <template v-slot:activator="{on}">
            <v-icon v-on="on">fa-tags</v-icon>
          </template>
          Tags
        </v-tooltip>
      </v-col>
      <v-col v-for="tag in displayedTags" :key="tag" class="shrink">
        <v-chip @click="setSearch(tag)" class="tag-search-link">
          <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
        </v-chip>
      </v-col>
      <v-col v-if="moreTags" class="shrink">
        <v-chip @click="showMore" class="show-more-tags">...</v-chip>
      </v-col>
      <v-col v-if="displayedTags.length === 0">
        <span>
          &nbsp;
          <span v-if="controls">No tags set. Please add some!</span>
          <span v-else>No tags set.</span>
        </span>
      </v-col>
      <ac-expanded-property v-model="toggle">
        <span slot="title">All Tags</span>
        <v-row>
          <v-col cols="12" v-if="editing && controls">
            <ac-patch-field field-type="ac-tag-field" :patcher="patcher" />
          </v-col>
          <v-col cols="12" v-show="!editing">
            <v-chip v-for="tag in patcher.rawValue" :key="tag" class="mx-1">
              <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
            </v-chip>
          </v-col>
        </v-row>
        <template slot="actions">
          <v-switch v-model="editing" label="Editing" v-if="controls" />
          <v-spacer />
          <v-btn color="primary" type="submit">
            Done
          </v-btn>
        </template>
      </ac-expanded-property>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcTagField from '@/components/fields/AcTagField.vue'
import {Prop} from 'vue-property-decorator'
import {Patch} from '@/store/singles/patcher'
import Subjective from '@/mixins/subjective'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {FormController} from '@/store/forms/form-controller'

  @Component({
    components: {AcLink, AcPatchField, AcExpandedProperty, AcTagField},
  })
export default class AcTagDisplay extends mixins(Subjective) {
    public searchForm: FormController = null as unknown as FormController
    @Prop({required: true})
    public patcher!: Patch
    @Prop({default: false})
    public editable!: boolean
    @Prop({required: true})
    public scope!: string

    public toggle = false
    public editing = false

    public editTags() {
      this.toggle = true
      this.editing = true
    }

    public showMore() {
      this.editing = false
      this.toggle = true
    }

    public setSearch(tag: string) {
      this.searchForm.reset()
      this.searchForm.fields.q.update(tag)
      this.$router.push(this.tagLink(tag))
    }
    public tagLink(tag: string) {
      return {name: 'Search' + this.scope, query: {q: tag}}
    }

    public get displayedTags() {
      return this.patcher.rawValue.slice(0, 10)
    }
    public get controls() {
      if (this.editable && this.isRegistered) {
        return true
      }
      if (this.isCurrent) {
        return true
      }
      return this.isStaff
    }
    public get moreTags() {
      return this.patcher.rawValue.length - this.displayedTags.length
    }
    public created() {
      this.searchForm = this.$getForm('search')
    }
}
</script>

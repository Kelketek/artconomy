<template>
  <v-flex>
    <ac-related-manager ref="manager" :list-controller="demoList" :field-controller="userForm.fields.user_id" item-key="user">
      <template v-slot:preview="{item}">
        <v-flex xs4 sm3 md2 lg1>
          <ac-avatar :user="item.x.user"
                     removable="true" @remove="item.delete().catch(userForm.setErrors)"/>
        </v-flex>
      </template>
      <template v-slot:default="{filter}">
        <ac-bound-field
            :field="userForm.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"/>
      </template>
    </ac-related-manager>
  </v-flex>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcRelatedManager from '../AcRelatedManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {ListController} from '@/store/lists/controller'
import {User} from '@/store/profiles/types/User'
import AcAvatar from '@/components/AcAvatar.vue'
import AcBoundField from '@/components/fields/AcBoundField'
  @Component({
    components: {AcBoundField, AcAvatar, AcRelatedManager},
  })
export default class DummyRelated extends Vue {
    public demoList: ListController<User> = null as unknown as ListController<User>
    public userForm: FormController = null as unknown as FormController
    public created() {
      this.demoList = this.$getList('demoList', {endpoint: '/endpoint/', paginated: false})
      this.userForm = this.$getForm('userForm', {endpoint: '/endpoint/', fields: {user_id: {value: null}}})
      this.demoList.get().then()
    }
}
</script>
